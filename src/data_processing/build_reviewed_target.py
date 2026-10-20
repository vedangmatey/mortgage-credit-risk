
"""
Create reviewed target sensitivity scenario.

Preserves V2 labels and flags loans with anomalous
status 99 observations inside the 24-month window.

The review policy applies only to the confirmed
ambiguous loan, not to every status 99 globally.
"""

from config.database import get_connection, PROJECT_ROOT

BASE = PROJECT_ROOT / "data/processed"
ORIG = BASE / "origination/origination_2007Q*.parquet"
PERF = BASE / "performance/performance_2007Q*.parquet"
SOURCE = BASE / "target/mortgage_target_2007_v2.parquet"
OUTPUT = BASE / "target/mortgage_target_2007_v3.parquet"


def sql_path(path):
    return path.as_posix().replace("'", "''")


def build():

    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)

    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    con = get_connection()

    try:
        con.execute(f"""
            COPY (
                WITH orig AS (
                    SELECT
                        col_20 AS loan_id,
                        TRY_CAST(SUBSTR(col_02, 1, 4)
                            AS INTEGER) * 12
                        + TRY_CAST(SUBSTR(col_02, 5, 2)
                            AS INTEGER) AS first_month
                    FROM read_parquet('{sql_path(ORIG)}')
                ),

                suspicious AS (
                    SELECT DISTINCT p.col_01 AS loan_id
                    FROM read_parquet('{sql_path(PERF)}') p
                    JOIN orig o ON p.col_01 = o.loan_id
                    WHERE TRIM(p.col_04) = '99'
                      AND (
                          TRY_CAST(SUBSTR(p.col_02, 1, 4)
                              AS INTEGER) * 12
                          + TRY_CAST(SUBSTR(p.col_02, 5, 2)
                              AS INTEGER)
                          - o.first_month
                      ) BETWEEN 0 AND 23
                ),

                flagged AS (
                    SELECT
                        v.*,
                        CASE
                            WHEN s.loan_id IS NOT NULL
                             AND v.payoff_adjusted_classification
                                 = 'EVENT'
                            THEN 1 ELSE 0
                        END AS status_99_review_flag
                    FROM read_parquet('{sql_path(SOURCE)}') v
                    LEFT JOIN suspicious s USING (loan_id)
                )

                SELECT
                    *,
                    CASE
                        WHEN status_99_review_flag = 1
                            THEN NULL
                        ELSE payoff_adjusted_target
                    END AS reviewed_target,

                    CASE
                        WHEN status_99_review_flag = 1
                            THEN 'UNRESOLVED_STATUS_99'
                        ELSE payoff_adjusted_classification
                    END AS reviewed_classification

                FROM flagged
            )
            TO '{sql_path(OUTPUT)}'
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        summary = con.execute("""
            SELECT
                reviewed_classification,
                COUNT(*) AS loans
            FROM read_parquet(?)
            GROUP BY 1
            ORDER BY loans DESC
        """, [str(OUTPUT)]).fetchall()

        actual = dict(summary)

        expected = {
            "COMPLETE_NON_EVENT": 828343,
            "CLEAN_PAYOFF_NON_EVENT": 256875,
            "UNRESOLVED": 93188,
            "EVENT": 59785,
            "UNRESOLVED_STATUS_99": 1,
        }

        print("\n========== REVIEWED TARGET V3 ==========")

        for label, count in summary:
            print(f"{label:<26}: {count:,}")

        assert actual == expected
        assert sum(actual.values()) == 1_238_192

        print(f"\nOutput: {OUTPUT}")
        print("Validation: PASSED")

    finally:
        con.close()


if __name__ == "__main__":
    build()
