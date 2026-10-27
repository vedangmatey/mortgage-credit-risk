
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]

TARGET = ROOT / "data" / "processed" / "target_preliminary.parquet"

con = duckdb.connect()

con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")

try:
    results = con.execute("""
        SELECT
            SUBSTR(loan_id, 1, 5) AS loan_cohort,

            COUNT(*) AS total_loans,

            COUNT(*) FILTER (
                WHERE target IS NOT NULL
            ) AS included_loans,

            COUNT(*) FILTER (
                WHERE target IS NULL
            ) AS excluded_loans,

            COUNT(*) FILTER (
                WHERE target = 1
            ) AS events,

            ROUND(
                100.0 * COUNT(*) FILTER (
                    WHERE target IS NULL
                ) / COUNT(*),
                2
            ) AS exclusion_rate_pct,

            ROUND(
                100.0 * COUNT(*) FILTER (
                    WHERE target = 1
                ) / NULLIF(
                    COUNT(*) FILTER (
                        WHERE target IS NOT NULL
                    ), 0
                ),
                2
            ) AS included_event_rate_pct

        FROM read_parquet(?)

        GROUP BY 1
        ORDER BY 1
    """, [str(TARGET)]).fetchall()

    print("========== POPULATION VALIDATION ==========")

    print(
        "Cohort | Total | Included | Excluded | "
        "Events | Exclusion % | Event %"
    )

    for row in results:
        print(
            f"{row[0]} | "
            f"{row[1]:,} | "
            f"{row[2]:,} | "
            f"{row[3]:,} | "
            f"{row[4]:,} | "
            f"{row[5]:.2f}% | "
            f"{row[6]:.2f}%"
        )

    assert len(results) == 4
    assert sum(r[1] for r in results) == 1_238_192
    assert sum(r[2] for r in results) == 888_123
    assert sum(r[3] for r in results) == 350_069
    assert sum(r[4] for r in results) == 59_785

    print("\nPopulation reconciliation: PASSED")

    
    # Step 106 — Compare included and excluded mortgage characteristics

    comparison = con.execute("""
        WITH loan_data AS (
            SELECT
                SUBSTR(o.column19, 1, 5) AS cohort,

                CASE
                    WHEN t.target IS NOT NULL THEN 'Included'
                    ELSE 'Excluded'
                END AS population,

                CASE
                    WHEN TRY_CAST(o.column00 AS DOUBLE)
                        BETWEEN 300 AND 850
                    THEN TRY_CAST(o.column00 AS DOUBLE)
                END AS credit_score,

                CASE
                    WHEN TRY_CAST(o.column11 AS DOUBLE)
                        BETWEEN 1 AND 105
                    THEN TRY_CAST(o.column11 AS DOUBLE)
                END AS ltv,

                CASE
                    WHEN TRY_CAST(o.column09 AS DOUBLE)
                        BETWEEN 1 AND 65
                    THEN TRY_CAST(o.column09 AS DOUBLE)
                END AS dti

            FROM read_parquet(
                'data/processed/orig_2007Q*.parquet'
            ) o

            JOIN read_parquet(
                'data/processed/target_preliminary.parquet'
            ) t
                ON o.column19 = t.loan_id
        )

        SELECT
            cohort,
            population,
            COUNT(*) AS mortgages,
            ROUND(AVG(credit_score), 2) AS avg_credit_score,
            ROUND(AVG(ltv), 2) AS avg_ltv,
            ROUND(AVG(dti), 2) AS avg_dti

        FROM loan_data
        GROUP BY cohort, population
        ORDER BY cohort, population
    """).df()

    print("\n========== SELECTION BIAS DIAGNOSTIC ==========")

    print(comparison.to_string(index=False))

    assert len(comparison) == 8
    assert comparison["mortgages"].sum() == 1_238_192

    print("\nPopulation comparison: PASSED")


    # Step 107 — Examine exclusion reasons and payoff flags

    exclusion_analysis = con.execute("""
        SELECT
            classification,
            payoff_flag,
            COUNT(*) AS mortgages
        FROM read_parquet(
            'data/processed/target_preliminary.parquet'
        )
        WHERE target IS NULL
        GROUP BY classification, payoff_flag
        ORDER BY mortgages DESC
    """).df()

    print("\n========== EXCLUSION ANALYSIS ==========")

    print(exclusion_analysis.to_string(index=False))

    assert exclusion_analysis["mortgages"].sum() == 350_069

    print("\nExclusion reconciliation: PASSED")


finally:
    con.close()
