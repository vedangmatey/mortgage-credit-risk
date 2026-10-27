
from pathlib import Path
import duckdb

# Step 108 — Early-payoff sensitivity dataset

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"

SOURCE = DATA / "target_preliminary.parquet"
PERFORMANCE = DATA / "perf_2007Q*.parquet"

OUTPUT = DATA / "target_payoff_sensitivity.parquet"
PENDING = DATA / "target_payoff_sensitivity.pending.parquet"

if OUTPUT.exists() or PENDING.exists():
    raise FileExistsError(
        "Sensitivity output already exists. "
        "Existing files will not be overwritten."
    )

con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")
con.execute(f"SET temp_directory='{(ROOT / 'data' / 'temp').as_posix()}'")

try:
    print("Building early-payoff sensitivity dataset...", flush=True)

    con.execute("""
        COPY (
            WITH candidates AS (
                SELECT
                    loan_id,
                    TRY_CAST(SUBSTR(first_payment_date, 1, 4)
                        AS INTEGER) * 12
                    + TRY_CAST(SUBSTR(first_payment_date, 5, 2)
                        AS INTEGER) AS first_month

                FROM read_parquet(?)

                WHERE classification = 'INCOMPLETE_HISTORY'
                  AND target IS NULL
                  AND payoff_flag = 1
            ),

            monthly AS (
                SELECT
                    p.column00 AS loan_id,

                    TRY_CAST(SUBSTR(p.column01, 1, 4)
                        AS INTEGER) * 12
                    + TRY_CAST(SUBSTR(p.column01, 5, 2)
                        AS INTEGER)
                    - c.first_month AS month_offset,

                    p.column03 AS delinquency_status,
                    p.column08 AS zero_balance_code

                FROM read_parquet(?) p

                INNER JOIN candidates c
                    ON p.column00 = c.loan_id
            ),

            history AS (
                SELECT *
                FROM monthly
                WHERE month_offset BETWEEN 0 AND 23
            ),

            summary AS (
                SELECT
                    loan_id,
                    COUNT(*) AS observed_months,
                    MIN(month_offset) AS first_offset,
                    MAX(month_offset) AS last_offset,

                    MIN(month_offset) FILTER (
                        WHERE zero_balance_code = '01'
                    ) AS payoff_offset,

                    MAX(CASE
                        WHEN TRY_CAST(delinquency_status AS INTEGER)
                            BETWEEN 3 AND 98
                        THEN 1 ELSE 0
                    END) AS serious_event,

                    MAX(CASE
                        WHEN delinquency_status IN ('99', 'RA')
                        THEN 1 ELSE 0
                    END) AS special_status

                FROM history
                GROUP BY loan_id
            ),

            eligible AS (
                SELECT loan_id
                FROM summary

                WHERE payoff_offset BETWEEN 0 AND 22
                  AND first_offset = 0
                  AND last_offset = payoff_offset
                  AND observed_months = payoff_offset + 1
                  AND serious_event = 0
                  AND special_status = 0
            )

            SELECT
                t.* REPLACE (
                    CASE
                        WHEN e.loan_id IS NOT NULL THEN 0
                        ELSE t.target
                    END AS target,

                    CASE
                        WHEN e.loan_id IS NOT NULL
                            THEN 'CLEAN_PAYOFF_NON_EVENT'
                        ELSE t.classification
                    END AS classification
                ),

                CASE
                    WHEN e.loan_id IS NOT NULL THEN 1
                    ELSE 0
                END AS sensitivity_payoff_flag

            FROM read_parquet(?) t
            LEFT JOIN eligible e
                ON t.loan_id = e.loan_id
        )
        TO ?
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """, [
        str(SOURCE),
        str(PERFORMANCE),
        str(SOURCE),
        str(PENDING)
    ])

    results = con.execute("""
        SELECT
            classification,
            COUNT(*) AS mortgages
        FROM read_parquet(?)
        GROUP BY classification
        ORDER BY mortgages DESC
    """, [str(PENDING)]).fetchall()

    print("\n========== SENSITIVITY TARGET ==========")

    for category, count in results:
        print(f"{category:<25}: {count:,}")

    checks = con.execute("""
        SELECT
            COUNT(*) AS total_loans,
            COUNT(DISTINCT loan_id) AS unique_loans,

            COUNT(*) FILTER (
                WHERE target = 1
            ) AS events,

            COUNT(*) FILTER (
                WHERE sensitivity_payoff_flag = 1
            ) AS clean_payoffs,

            COUNT(*) FILTER (
                WHERE target IS NOT NULL
            ) AS modeling_population

        FROM read_parquet(?)
    """, [str(PENDING)]).fetchone()

    assert checks[0] == 1_238_192
    assert checks[1] == 1_238_192
    assert checks[2] == 59_785
    assert 0 <= checks[3] <= 256_875
    assert checks[4] == 888_123 + checks[3]

    # Independently confirm that no other targets changed
    invalid_changes = con.execute("""
        SELECT COUNT(*)
        FROM read_parquet(?) original
        JOIN read_parquet(?) sensitivity
          ON original.loan_id = sensitivity.loan_id
        WHERE original.target IS DISTINCT FROM sensitivity.target
          AND NOT (
              original.target IS NULL
              AND sensitivity.target = 0
              AND sensitivity.sensitivity_payoff_flag = 1
          )
    """, [str(SOURCE), str(PENDING)]).fetchone()[0]

    assert invalid_changes == 0

    PENDING.rename(OUTPUT)

    print(f"\nClean payoffs added : {checks[3]:,}")
    print(f"Modeling population : {checks[4]:,}")
    print(f"Output: {OUTPUT}")
    print("Sensitivity validation: PASSED")

finally:
    con.close()
