
"""
Cross-file validation for the payoff-adjusted target.

Verifies:
1. Both datasets have unique loan identifiers.
2. All original target information is preserved.
3. Clean-payoff flags satisfy the documented rules.
4. Adjusted labels are consistent with those flags.
"""

from config.database import get_connection, PROJECT_ROOT

TARGET_DIR = PROJECT_ROOT / "data/processed/target"

SOURCE = TARGET_DIR / "mortgage_target_2007.parquet"
ADJUSTED = TARGET_DIR / "mortgage_target_2007_v2.parquet"


def validate():

    con = get_connection()

    try:
        for path in (SOURCE, ADJUSTED):
            if not path.is_file():
                raise FileNotFoundError(path)

            total, unique = con.execute("""
                SELECT COUNT(*), COUNT(DISTINCT loan_id)
                FROM read_parquet(?)
            """, [str(path)]).fetchone()

            assert total == unique == 1_238_192, (
                f"Invalid loan count or duplicate IDs: {path}"
            )

        result = con.execute("""
            SELECT
                COUNT(*) AS matched_loans,

                COUNT(*) FILTER (
                    WHERE
                        a.preliminary_target
                            IS DISTINCT FROM s.preliminary_target
                        OR a.classification
                            IS DISTINCT FROM s.classification
                        OR a.observed_months
                            IS DISTINCT FROM s.observed_months
                        OR a.first_serious_delinquency_month
                            IS DISTINCT FROM s.first_serious_delinquency_month
                        OR a.first_zero_balance_code
                            IS DISTINCT FROM s.first_zero_balance_code
                ) AS altered_original_fields,

                COUNT(*) FILTER (
                    WHERE a.clean_payoff_flag IS DISTINCT FROM
                        CASE
                            WHEN s.classification = 'UNRESOLVED'
                              AND s.first_zero_balance_code = '01'
                              AND s.first_observed_offset = 0
                              AND s.observed_months =
                                  s.last_observed_offset + 1
                              AND s.reo_status_observed = 0
                              AND s.last_observed_offset = (
                                  TRY_CAST(SUBSTR(
                                      s.first_zero_balance_effective_date,
                                      1, 4
                                  ) AS INTEGER) * 12
                                  + TRY_CAST(SUBSTR(
                                      s.first_zero_balance_effective_date,
                                      5, 2
                                  ) AS INTEGER)
                                  - TRY_CAST(SUBSTR(
                                      s.first_payment_date,
                                      1, 4
                                  ) AS INTEGER) * 12
                                  - TRY_CAST(SUBSTR(
                                      s.first_payment_date,
                                      5, 2
                                  ) AS INTEGER)
                              )
                            THEN 1 ELSE 0
                        END
                ) AS invalid_payoff_flags,

                COUNT(*) FILTER (
                    WHERE a.payoff_adjusted_target IS DISTINCT FROM
                        CASE WHEN a.clean_payoff_flag = 1
                             THEN 0 ELSE s.preliminary_target END
                ) AS invalid_adjusted_targets,

                COUNT(*) FILTER (
                    WHERE a.payoff_adjusted_classification
                        IS DISTINCT FROM
                        CASE WHEN a.clean_payoff_flag = 1
                             THEN 'CLEAN_PAYOFF_NON_EVENT'
                             ELSE s.classification END
                ) AS invalid_adjusted_classes,

                COUNT(*) FILTER (
                    WHERE a.clean_payoff_flag = 1
                ) AS clean_payoffs

            FROM read_parquet(?) s
            JOIN read_parquet(?) a USING (loan_id)
        """, [str(SOURCE), str(ADJUSTED)]).fetchone()

        labels = [
            "Matched loans",
            "Altered original fields",
            "Invalid payoff flags",
            "Invalid adjusted targets",
            "Invalid adjusted classes",
            "Clean payoff loans"
        ]

        print("\n========== ADJUSTED TARGET VALIDATION ==========")

        for label, value in zip(labels, result):
            print(f"{label:<27}: {value:,}")

        assert result == (
            1_238_192,
            0,
            0,
            0,
            0,
            256_875
        ), "Adjusted target validation FAILED"

        print("\nFinal status: PASSED")

    finally:
        con.close()


if __name__ == "__main__":
    validate()
