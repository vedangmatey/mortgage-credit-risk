
"""
Freddie Mac Mortgage Credit Risk Project

Build preliminary 24-month serious-delinquency targets.

Target:
    1    = Observed 90+ days delinquent within 24 months
    0    = No event and all 24 reporting months observed
    NULL = Incomplete observation without a qualifying event

Also preserves termination information and observation flags.

These are preliminary research labels, not yet approved
final modeling outcomes.
"""

from pathlib import Path
import time

from config.database import get_connection, PROJECT_ROOT


ORIG_PATH = (
    PROJECT_ROOT / "data/processed/origination"
    / "origination_2007Q*.parquet"
)

PERF_PATH = (
    PROJECT_ROOT / "data/processed/performance"
    / "performance_2007Q*.parquet"
)

OUTPUT_DIR = PROJECT_ROOT / "data/processed/target"
OUTPUT_FILE = OUTPUT_DIR / "mortgage_target_2007.parquet"
PENDING_FILE = OUTPUT_DIR / "mortgage_target_2007.pending.parquet"


def sql_path(path: Path) -> str:
    """Escape local paths for DuckDB SQL string literals."""
    return path.as_posix().replace("'", "''")


def build_target():

    start = time.perf_counter()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"Output already exists: {OUTPUT_FILE}"
        )

    if PENDING_FILE.exists():
        raise FileExistsError(
            f"Incomplete output exists: {PENDING_FILE}"
        )

    for pattern in (ORIG_PATH, PERF_PATH):
        if len(list(pattern.parent.glob(pattern.name))) != 4:
            raise FileNotFoundError(
                f"Expected four quarterly files: {pattern}"
            )

    con = get_connection()

    try:
        print("Building loan-level target dataset...", flush=True)

        orig = sql_path(ORIG_PATH)
        perf = sql_path(PERF_PATH)
        output = sql_path(PENDING_FILE)

        con.execute(f"""
            COPY (
                WITH orig AS (
                    SELECT
                        col_20 AS loan_id,
                        col_02 AS first_payment_date,

                        TRY_CAST(
                            SUBSTR(col_02, 1, 4) AS INTEGER
                        ) * 12
                        + TRY_CAST(
                            SUBSTR(col_02, 5, 2) AS INTEGER
                        ) AS first_payment_month

                    FROM read_parquet('{orig}')
                ),

                perf_window AS (
                    SELECT
                        p.col_01 AS loan_id,

                        (
                            TRY_CAST(
                                SUBSTR(p.col_02, 1, 4) AS INTEGER
                            ) * 12
                            + TRY_CAST(
                                SUBSTR(p.col_02, 5, 2) AS INTEGER
                            )
                            - o.first_payment_month
                        ) AS month_offset,

                        TRY_CAST(
                            p.col_04 AS INTEGER
                        ) AS delinquency_status,

                        TRIM(p.col_04) AS raw_status,

                        NULLIF(
                            TRIM(p.col_09), ''
                        ) AS zero_balance_code,

                        NULLIF(
                            TRIM(p.col_10), ''
                        ) AS zero_balance_effective_date

                    FROM read_parquet('{perf}') p

                    JOIN orig o
                        ON p.col_01 = o.loan_id

                    WHERE (
                        TRY_CAST(
                            SUBSTR(p.col_02, 1, 4) AS INTEGER
                        ) * 12
                        + TRY_CAST(
                            SUBSTR(p.col_02, 5, 2) AS INTEGER
                        )
                        - o.first_payment_month
                    ) BETWEEN 0 AND 23
                ),

                loan_summary AS (
                    SELECT
                        loan_id,

                        COUNT(DISTINCT month_offset)
                            AS observed_months,

                        MIN(month_offset)
                            AS first_observed_offset,

                        MAX(month_offset)
                            AS last_observed_offset,

                        MIN(month_offset) FILTER (
                            WHERE delinquency_status >= 3
                        ) AS first_serious_delinquency_offset,

                        MAX(
                            CASE
                                WHEN raw_status = 'RA' THEN 1
                                ELSE 0
                            END
                        ) AS reo_status_observed,

                        ARG_MIN(
                            zero_balance_code,
                            month_offset
                        ) AS first_zero_balance_code,

                        ARG_MIN(
                            zero_balance_effective_date,
                            month_offset
                        ) FILTER (
                            WHERE zero_balance_code IS NOT NULL
                        ) AS first_zero_balance_effective_date

                    FROM perf_window
                    GROUP BY loan_id
                ),

                classified AS (
                    SELECT
                        o.loan_id,
                        o.first_payment_date,

                        COALESCE(s.observed_months, 0)
                            AS observed_months,

                        s.first_observed_offset,
                        s.last_observed_offset,

                        s.first_serious_delinquency_offset,

                        CASE
                            WHEN s.first_serious_delinquency_offset
                                 IS NOT NULL
                            THEN s.first_serious_delinquency_offset + 1
                        END AS first_serious_delinquency_month,

                        COALESCE(s.reo_status_observed, 0)
                            AS reo_status_observed,

                        s.first_zero_balance_code,
                        s.first_zero_balance_effective_date,

                        CASE
                            WHEN s.first_serious_delinquency_offset
                                 IS NOT NULL THEN 1

                            WHEN COALESCE(s.observed_months, 0) = 24
                                THEN 0

                            ELSE NULL
                        END AS preliminary_target,

                        CASE
                            WHEN s.first_serious_delinquency_offset
                                 IS NOT NULL
                                THEN 'EVENT'

                            WHEN COALESCE(s.observed_months, 0) = 24
                                THEN 'COMPLETE_NON_EVENT'

                            ELSE 'UNRESOLVED'
                        END AS classification

                    FROM orig o
                    LEFT JOIN loan_summary s
                        ON o.loan_id = s.loan_id
                )

                SELECT * FROM classified
            )
            TO '{output}'
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        print("Validating target dataset...", flush=True)

        result = con.execute("""
            SELECT
                COUNT(*) AS total_loans,
                COUNT(DISTINCT loan_id) AS unique_loans,

                COUNT(*) FILTER (
                    WHERE classification = 'EVENT'
                ) AS events,

                COUNT(*) FILTER (
                    WHERE classification = 'COMPLETE_NON_EVENT'
                ) AS non_events,

                COUNT(*) FILTER (
                    WHERE classification = 'UNRESOLVED'
                ) AS unresolved,

                COUNT(*) FILTER (
                    WHERE preliminary_target IS NULL
                ) AS null_targets

            FROM read_parquet(?)
        """, [str(PENDING_FILE)]).fetchone()

        (
            total,
            unique,
            events,
            non_events,
            unresolved,
            null_targets
        ) = result

        if total != 1_238_192:
            raise ValueError("Unexpected total loan count")

        if unique != total:
            raise ValueError("Duplicate loan identifiers detected")

        if events + non_events + unresolved != total:
            raise ValueError("Target classification mismatch")

        if null_targets != unresolved:
            raise ValueError("Unresolved target mismatch")

        # Reconcile with the previously verified EDA counts.
        if (events, non_events, unresolved) != (
            59_786, 828_343, 350_063
        ):
            raise ValueError(
                "Target counts differ from the EDA results"
            )

        con.close()
        con = None

        PENDING_FILE.rename(OUTPUT_FILE)

        elapsed = time.perf_counter() - start

        print("\n========== TARGET GENERATION ==========")
        print(f"Total loans       : {total:,}")
        print(f"Unique loans      : {unique:,}")
        print(f"Events            : {events:,}")
        print(f"Complete non-event: {non_events:,}")
        print(f"Unresolved        : {unresolved:,}")
        print(f"Parquet size (MB) : {OUTPUT_FILE.stat().st_size / 1024**2:.2f}")
        print(f"Processing seconds: {elapsed:.2f}")
        print(f"Output            : {OUTPUT_FILE}")
        print("Validation        : PASSED")

    finally:
        if con is not None:
            con.close()


if __name__ == "__main__":
    build_target()
