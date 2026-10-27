
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
            + CAST(SUBSTR(column01, 5, 2) AS INT)
                AS first_month
        FROM read_parquet(
            'data/processed/orig_2007Q*.parquet'
        )
    ),

    coverage AS (
        SELECT
            p.column00 AS loan_id,
            COUNT(*) AS months_observed
        FROM read_parquet(
            'data/processed/perf_2007Q*.parquet'
        ) p
        JOIN orig o ON p.column00 = o.loan_id
        WHERE (
            CAST(SUBSTR(p.column01, 1, 4) AS INT) * 12
            + CAST(SUBSTR(p.column01, 5, 2) AS INT)
            - o.first_month
        ) BETWEEN 0 AND 23
        GROUP BY p.column00
    )

    SELECT
        COUNT(*) FILTER (
            WHERE t.observed_serious_event = 1
        ) AS observed_events,

        COUNT(*) FILTER (
            WHERE t.observed_serious_event = 0
              AND c.months_observed = 24
        ) AS complete_non_events,

        COUNT(*) FILTER (
            WHERE t.observed_serious_event = 0
              AND COALESCE(c.months_observed, 0) < 24
        ) AS incomplete_non_events

    FROM read_parquet(
        'data/processed/target_events.parquet'
    ) t

    LEFT JOIN coverage c ON t.loan_id = c.loan_id
""").fetchone()

print("Observed serious events :", f"{result[0]:,}")
print("Complete non-events    :", f"{result[1]:,}")
print("Incomplete non-events  :", f"{result[2]:,}")

assert sum(result) == 1_238_192
print("\nReconciliation: PASSED")



# Step 76 — Check special statuses in complete non-events

special_statuses = con.execute("""
    WITH orig AS (
        SELECT
            column19 AS loan_id,
            CAST(SUBSTR(column01, 1, 4) AS INT) * 12
            + CAST(SUBSTR(column01, 5, 2) AS INT)
                AS first_month
        FROM read_parquet(
            'data/processed/orig_2007Q*.parquet'
        )
    ),

    loan_history AS (
        SELECT
            p.column00 AS loan_id,
            COUNT(*) AS observed_months,
            MAX(CASE WHEN p.column03 = '99'
                THEN 1 ELSE 0 END) AS has_99,
            MAX(CASE WHEN p.column03 = 'RA'
                THEN 1 ELSE 0 END) AS has_ra

        FROM read_parquet(
            'data/processed/perf_2007Q*.parquet'
        ) p

        JOIN orig o ON p.column00 = o.loan_id

        WHERE (
            CAST(SUBSTR(p.column01, 1, 4) AS INT) * 12
            + CAST(SUBSTR(p.column01, 5, 2) AS INT)
            - o.first_month
        ) BETWEEN 0 AND 23

        GROUP BY p.column00
    )

    SELECT
        COUNT(*) AS complete_non_event_candidates,
        SUM(h.has_99) AS loans_with_99,
        SUM(h.has_ra) AS loans_with_ra

    FROM loan_history h

    JOIN read_parquet(
        'data/processed/target_events.parquet'
    ) t ON h.loan_id = t.loan_id

    WHERE h.observed_months = 24
      AND t.observed_serious_event = 0

""").fetchone()

print("\n========== SPECIAL STATUS AUDIT ==========")
print("Complete non-event candidates:", f"{special_statuses[0]:,}")
print("Loans with status 99         :", f"{special_statuses[1]:,}")
print("Loans with status RA         :", f"{special_statuses[2]:,}")

assert special_statuses[0] == 828_344

print("Special status reconciliation: PASSED")


con.close()
