
"""
Independent validation of reviewed mortgage target V3.

Checks:
1. Original V2 columns remain unchanged.
2. Exactly one loan is flagged for status 99 review.
3. Reviewed targets and classifications are consistent.
4. The flagged loan has at least one status 99 record
   within the first 24 scheduled payment months.
5. The flagged loan has no other confirmed numeric
   serious-delinquency status (03 through 98)
   within the first 24 months.
"""

from config.database import get_connection, PROJECT_ROOT


BASE = PROJECT_ROOT / "data/processed"

V2 = BASE / "target/mortgage_target_2007_v2.parquet"
V3 = BASE / "target/mortgage_target_2007_v3.parquet"

PERF = BASE / "performance/performance_2007Q*.parquet"


def validate():

    for path in (V2, V3):
        if not path.is_file():
            raise FileNotFoundError(path)

    if len(list(PERF.parent.glob(PERF.name))) != 4:
        raise FileNotFoundError(
            "Expected four quarterly performance files"
        )

    con = get_connection()

    try:
        print("========== V3 INDEPENDENT VALIDATION ==========")

        # -------------------------------------------------
        # 1. Confirm original V2 data was preserved
        # -------------------------------------------------

        changed = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT *
                FROM read_parquet(?)

                EXCEPT ALL

                SELECT * EXCLUDE (
                    status_99_review_flag,
                    reviewed_target,
                    reviewed_classification
                )
                FROM read_parquet(?)
            )
        """, [str(V2), str(V3)]).fetchone()[0]

        reverse_changed = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT * EXCLUDE (
                    status_99_review_flag,
                    reviewed_target,
                    reviewed_classification
                )
                FROM read_parquet(?)

                EXCEPT ALL

                SELECT *
                FROM read_parquet(?)
            )
        """, [str(V3), str(V2)]).fetchone()[0]

        # -------------------------------------------------
        # 2. Validate loan counts, flags, and target values
        # -------------------------------------------------

        summary = con.execute("""
            SELECT
                COUNT(*) AS total,

                COUNT(DISTINCT loan_id) AS unique_loans,

                COUNT(*) FILTER (
                    WHERE status_99_review_flag = 1
                ) AS flagged,

                COUNT(*) FILTER (
                    WHERE status_99_review_flag IS NULL
                       OR status_99_review_flag NOT IN (0, 1)
                ) AS invalid_flags,

                COUNT(*) FILTER (
                    WHERE status_99_review_flag = 1
                      AND (
                          reviewed_target IS NOT NULL
                          OR payoff_adjusted_classification <> 'EVENT'
                      )
                ) AS invalid_flagged_target,

                COUNT(*) FILTER (
                    WHERE status_99_review_flag = 1
                      AND reviewed_classification
                          IS DISTINCT FROM 'UNRESOLVED_STATUS_99'
                ) AS invalid_flagged_classification,

                COUNT(*) FILTER (
                    WHERE status_99_review_flag = 0
                      AND (
                          reviewed_target
                              IS DISTINCT FROM payoff_adjusted_target

                          OR reviewed_classification
                              IS DISTINCT FROM payoff_adjusted_classification
                      )
                ) AS invalid_unflagged

            FROM read_parquet(?)
        """, [str(V3)]).fetchone()

        (
            total,
            unique,
            flagged,
            invalid_flags,
            invalid_target,
            invalid_class,
            invalid_unflagged
        ) = summary

        print(f"Total loans              : {total:,}")
        print(f"Unique loans             : {unique:,}")
        print(f"V2 rows missing from V3  : {changed:,}")
        print(f"V3 original rows changed : {reverse_changed:,}")
        print(f"Status 99 review flags   : {flagged:,}")
        print(f"Invalid flag values      : {invalid_flags:,}")
        print(f"Invalid flagged targets  : {invalid_target:,}")
        print(f"Invalid flagged classes  : {invalid_class:,}")
        print(f"Invalid unflagged rows   : {invalid_unflagged:,}")

        assert total == unique == 1_238_192, (
            "Loan count or uniqueness validation failed"
        )

        assert changed == reverse_changed == 0, (
            "Original V2 data was modified"
        )

        assert flagged == 1, (
            "Expected exactly one flagged mortgage"
        )

        assert (
            invalid_flags == 0
            and invalid_target == 0
            and invalid_class == 0
            and invalid_unflagged == 0
        ), "Target classification validation failed"

        # -------------------------------------------------
        # 3. Identify the flagged mortgage
        # -------------------------------------------------

        loan = con.execute("""
            SELECT
                loan_id,
                first_payment_date

            FROM read_parquet(?)

            WHERE status_99_review_flag = 1
        """, [str(V3)]).fetchone()

        loan_id, first_payment = loan

        # -------------------------------------------------
        # 4. Independently inspect monthly performance
        # -------------------------------------------------

        history = con.execute("""
            WITH records AS (
                SELECT
                    TRY_CAST(col_04 AS INTEGER) AS status

                FROM read_parquet(?)

                WHERE col_01 = ?

                  AND (
                      TRY_CAST(
                          SUBSTR(col_02, 1, 4)
                          AS INTEGER
                      ) * 12

                      + TRY_CAST(
                          SUBSTR(col_02, 5, 2)
                          AS INTEGER
                      )

                      - TRY_CAST(
                          SUBSTR(?, 1, 4)
                          AS INTEGER
                      ) * 12

                      - TRY_CAST(
                          SUBSTR(?, 5, 2)
                          AS INTEGER
                      )
                  ) BETWEEN 0 AND 23
            )

            SELECT
                COUNT(*) FILTER (
                    WHERE status = 99
                ) AS status_99_records,

                COUNT(*) FILTER (
                    WHERE status BETWEEN 3 AND 98
                ) AS other_serious_records

            FROM records
        """, [
            str(PERF),
            loan_id,
            first_payment,
            first_payment
        ]).fetchone()

        status_99, other_serious = history

        print(f"Flagged loan status 99   : {status_99:,}")
        print(f"Other serious statuses   : {other_serious:,}")

        # -------------------------------------------------
        # 5. Corrected status 99 validation
        # -------------------------------------------------

        # Multiple status 99 records may belong to
        # the same flagged mortgage.

        assert status_99 >= 1, (
            "Flagged mortgage has no status 99 observations"
        )

        assert other_serious == 0, (
            "Flagged mortgage has another confirmed "
            "serious-delinquency observation"
        )

        print("\nFinal status: PASSED")

    finally:
        con.close()


if __name__ == "__main__":
    validate()
