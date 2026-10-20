
"""
Build payoff-adjusted mortgage target scenario.

Preserves the original target and adds:
- clean_payoff_flag
- payoff_adjusted_target
- payoff_adjusted_classification

This scenario is subject to further model validation.
"""

from config.database import get_connection, PROJECT_ROOT


TARGET_DIR = PROJECT_ROOT / "data/processed/target"

SOURCE = TARGET_DIR / "mortgage_target_2007.parquet"
OUTPUT = TARGET_DIR / "mortgage_target_2007_v2.parquet"


def build_adjusted_target():

    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)

    con = get_connection()

    try:
        source = SOURCE.as_posix().replace("'", "''")
        output = OUTPUT.as_posix().replace("'", "''")

        con.execute(f"""
            COPY (
                WITH flagged AS (
                    SELECT
                        *,

                        CASE
                            WHEN classification = 'UNRESOLVED'
                             AND first_zero_balance_code = '01'
                             AND first_observed_offset = 0
                             AND observed_months = last_observed_offset + 1
                             AND last_observed_offset = (
                                 TRY_CAST(
                                     SUBSTR(first_zero_balance_effective_date, 1, 4)
                                     AS INTEGER
                                 ) * 12
                                 + TRY_CAST(
                                     SUBSTR(first_zero_balance_effective_date, 5, 2)
                                     AS INTEGER
                                 )
                                 - TRY_CAST(
                                     SUBSTR(first_payment_date, 1, 4)
                                     AS INTEGER
                                 ) * 12
                                 - TRY_CAST(
                                     SUBSTR(first_payment_date, 5, 2)
                                     AS INTEGER
                                 )
                             )
                             AND reo_status_observed = 0
                            THEN 1
                            ELSE 0
                        END AS clean_payoff_flag

                    FROM read_parquet('{source}')
                )

                SELECT
                    *,

                    CASE
                        WHEN clean_payoff_flag = 1 THEN 0
                        ELSE preliminary_target
                    END AS payoff_adjusted_target,

                    CASE
                        WHEN clean_payoff_flag = 1
                            THEN 'CLEAN_PAYOFF_NON_EVENT'
                        ELSE classification
                    END AS payoff_adjusted_classification

                FROM flagged
            )
            TO '{output}'
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        result = con.execute("""
            SELECT
                COUNT(*) AS total,
                COUNT(DISTINCT loan_id) AS unique_loans,

                COUNT(*) FILTER (
                    WHERE payoff_adjusted_classification = 'EVENT'
                ) AS events,

                COUNT(*) FILTER (
                    WHERE payoff_adjusted_classification = 'COMPLETE_NON_EVENT'
                ) AS complete_non_events,

                COUNT(*) FILTER (
                    WHERE payoff_adjusted_classification = 'CLEAN_PAYOFF_NON_EVENT'
                ) AS clean_payoffs,

                COUNT(*) FILTER (
                    WHERE payoff_adjusted_classification = 'UNRESOLVED'
                ) AS unresolved,

                COUNT(*) FILTER (
                    WHERE clean_payoff_flag = 1
                ) AS payoff_flags,

                COUNT(*) FILTER (
                    WHERE payoff_adjusted_target IS NULL
                ) AS missing_targets

            FROM read_parquet(?)
        """, [str(OUTPUT)]).fetchone()

        expected = (
            1_238_192,
            1_238_192,
            59_786,
            828_343,
            256_875,
            93_188,
            256_875,
            93_188
        )

        print("\n========== ADJUSTED TARGET SUMMARY ==========")

        labels = [
            "Total loans",
            "Unique loans",
            "Events",
            "Complete non-events",
            "Clean payoffs",
            "Unresolved",
            "Clean payoff flags",
            "Missing adjusted targets"
        ]

        for label, value in zip(labels, result):
            print(f"{label:<26}: {value:,}")

        if result != expected:
            raise ValueError("Adjusted target validation FAILED")

        print(f"\nOutput: {OUTPUT}")
        print("Validation: PASSED")

    finally:
        con.close()


if __name__ == "__main__":
    build_adjusted_target()
