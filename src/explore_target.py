
import duckdb

con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")
con.execute("SET temp_directory='data/temp'")

result = con.execute("""
    WITH orig AS (
        SELECT
            column19 AS loan_id,
            CAST(SUBSTR(column01, 1, 4) AS INT) * 12
            + CAST(SUBSTR(column01, 5, 2) AS INT) AS first_month
        FROM read_parquet('data/processed/orig_2007Q*.parquet')
    ),

    monthly AS (
        SELECT
            p.column00 AS loan_id,
            CAST(SUBSTR(p.column01, 1, 4) AS INT) * 12
            + CAST(SUBSTR(p.column01, 5, 2) AS INT)
            - o.first_month AS month_offset,
            p.column08 AS payoff_code,
            TRY_CAST(p.column03 AS INT) AS status
        FROM read_parquet('data/processed/perf_2007Q*.parquet') p
        JOIN orig o ON p.column00 = o.loan_id
        WHERE (
            CAST(SUBSTR(p.column01, 1, 4) AS INT) * 12
            + CAST(SUBSTR(p.column01, 5, 2) AS INT)
            - o.first_month
        ) BETWEEN 0 AND 23
    ),

    summary AS (
        SELECT
            loan_id,
            COUNT(DISTINCT month_offset) AS observed_months,
            MIN(month_offset) AS first_offset,
            MAX(month_offset) AS last_offset,
            MIN(month_offset) FILTER (
                WHERE payoff_code = '01'
            ) AS payoff_offset,
            MAX(CASE WHEN status BETWEEN 3 AND 98
                THEN 1 ELSE 0 END) AS serious
        FROM monthly
        GROUP BY loan_id
    )

    SELECT
        CASE
            WHEN first_offset > 0
                THEN 'Late reporting start'
            WHEN observed_months = 24
                THEN 'Full 24-month coverage'
            WHEN observed_months = payoff_offset + 1
              AND last_offset = payoff_offset
                THEN 'Continuous through payoff'
            ELSE 'Gaps or timing differences'
        END AS category,
        COUNT(*) AS mortgages
    FROM summary
    WHERE payoff_offset IS NOT NULL
      AND serious = 0
    GROUP BY 1
    ORDER BY mortgages DESC
""").fetchall()

print("========== PAYOFF COVERAGE ==========")

for category, count in result:
    print(f"{category}: {count:,}")

assert sum(count for _, count in result) == 290_861
print("\nValidation: PASSED")

con.close()
