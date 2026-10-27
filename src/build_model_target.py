
from pathlib import Path
import duckdb

# ---------------------------------------
# 1. Project paths
# ---------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"

ORIG = (DATA / "orig_2007Q*.parquet").as_posix()
PERF = (DATA / "perf_2007Q*.parquet").as_posix()

OUTPUT = DATA / "target_preliminary.parquet"
PENDING = DATA / "target_preliminary.pending.parquet"

if OUTPUT.exists() or PENDING.exists():
    raise FileExistsError(
        "Target output already exists. "
        "Existing results will not be overwritten."
    )

# ---------------------------------------
# 2. Connect to DuckDB
# ---------------------------------------

con = duckdb.connect()

con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")
con.execute("SET temp_directory='data/temp'")

print("Building mortgage-level target...", flush=True)

try:

    # ---------------------------------------
    # 3. Create target classifications
    # ---------------------------------------

    con.execute(f"""
        COPY (
            WITH origination AS (
                SELECT
                    column19 AS loan_id,
                    column01 AS first_payment_date,

                    TRY_CAST(SUBSTR(column01, 1, 4)
                        AS INTEGER) * 12
                    + TRY_CAST(SUBSTR(column01, 5, 2)
                        AS INTEGER) AS first_month

                FROM read_parquet('{ORIG}')
            ),

            monthly_history AS (
                SELECT
                    p.column00 AS loan_id,
                    p.column01 AS reporting_month,
                    p.column03 AS delinquency_status,
                    p.column08 AS zero_balance_code

                FROM read_parquet('{PERF}') p

                JOIN origination o
                    ON p.column00 = o.loan_id

                WHERE (
                    TRY_CAST(SUBSTR(p.column01, 1, 4)
                        AS INTEGER) * 12
                    + TRY_CAST(SUBSTR(p.column01, 5, 2)
                        AS INTEGER)
                    - o.first_month
                ) BETWEEN 0 AND 23
            ),

            history_summary AS (
                SELECT
                    loan_id,

                    COUNT(*) AS observed_months,

                    MAX(CASE
                        WHEN TRY_CAST(delinquency_status
                            AS INTEGER) BETWEEN 3 AND 98
                        THEN 1 ELSE 0
                    END) AS serious_event,

                    MAX(CASE
                        WHEN delinquency_status = '99'
                        THEN 1 ELSE 0
                    END) AS has_status_99,

                    MAX(CASE
                        WHEN delinquency_status = 'RA'
                        THEN 1 ELSE 0
                    END) AS has_status_ra,

                    MAX(CASE
                        WHEN zero_balance_code = '01'
                        THEN 1 ELSE 0
                    END) AS payoff_flag

                FROM monthly_history
                GROUP BY loan_id
            ),

            combined AS (
                SELECT
                    o.loan_id,
                    o.first_payment_date,

                    COALESCE(h.observed_months, 0)
                        AS observed_months,

                    COALESCE(h.serious_event, 0)
                        AS serious_event,

                    COALESCE(h.has_status_99, 0)
                        AS has_status_99,

                    COALESCE(h.has_status_ra, 0)
                        AS has_status_ra,

                    COALESCE(h.payoff_flag, 0)
                        AS payoff_flag

                FROM origination o

                LEFT JOIN history_summary h
                    ON o.loan_id = h.loan_id
            )

            SELECT
                *,

                CASE
                    WHEN serious_event = 1 THEN 1

                    WHEN has_status_99 = 1
                      OR has_status_ra = 1
                        THEN NULL

                    WHEN observed_months = 24 THEN 0

                    ELSE NULL
                END AS target,

                CASE
                    WHEN serious_event = 1
                        THEN 'EVENT'

                    WHEN has_status_99 = 1
                      OR has_status_ra = 1
                        THEN 'SPECIAL_STATUS_REVIEW'

                    WHEN observed_months = 24
                        THEN 'COMPLETE_NON_EVENT'

                    ELSE 'INCOMPLETE_HISTORY'
                END AS classification

            FROM combined
        )
        TO '{PENDING.as_posix()}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    # ---------------------------------------
    # 4. Validate results
    # ---------------------------------------

    result = con.execute("""
        SELECT
            classification,
            COUNT(*) AS loans
        FROM read_parquet(?)
        GROUP BY classification
        ORDER BY classification
    """, [str(PENDING)]).fetchall()

    print("\n========== TARGET SUMMARY ==========")

    for category, count in result:
        print(f"{category:<24}: {count:,}")

    totals = con.execute("""
        SELECT
            COUNT(*),
            COUNT(DISTINCT loan_id),
            COUNT(*) FILTER (WHERE target = 1),
            COUNT(*) FILTER (
                WHERE target = 0 AND observed_months <> 24
            )
        FROM read_parquet(?)
    """, [str(PENDING)]).fetchone()

    assert totals[0] == 1_238_192
    assert totals[1] == 1_238_192
    assert totals[2] == 59_785
    assert totals[3] == 0

    # Finalize only after validation passes
    PENDING.rename(OUTPUT)

    print(f"\nOutput: {OUTPUT}")
    print("Target validation: PASSED")

finally:
    con.close()
