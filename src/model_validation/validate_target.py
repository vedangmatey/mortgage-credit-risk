
"""
Independent consistency checks for preliminary
mortgage serious-delinquency targets.
"""

from config.database import get_connection, PROJECT_ROOT


TARGET_PATH = (
    PROJECT_ROOT
    / "data/processed/target/mortgage_target_2007.parquet"
)


def validate_target():

    if not TARGET_PATH.is_file():
        raise FileNotFoundError(TARGET_PATH)

    con = get_connection()

    try:
        result = con.execute("""
            SELECT
                COUNT(*) AS total_loans,
                COUNT(DISTINCT loan_id) AS unique_loans,

                COUNT(*) FILTER (
                    WHERE classification = 'EVENT'
                      AND (
                          preliminary_target IS DISTINCT FROM 1
                          OR first_serious_delinquency_month
                             NOT BETWEEN 1 AND 24
                          OR first_serious_delinquency_month IS NULL
                      )
                ) AS invalid_events,

                COUNT(*) FILTER (
                    WHERE classification = 'COMPLETE_NON_EVENT'
                      AND (
                          preliminary_target IS DISTINCT FROM 0
                          OR observed_months <> 24
                          OR first_serious_delinquency_month IS NOT NULL
                      )
                ) AS invalid_non_events,

                COUNT(*) FILTER (
                    WHERE classification = 'UNRESOLVED'
                      AND (
                          preliminary_target IS NOT NULL
                          OR observed_months >= 24
                          OR first_serious_delinquency_month IS NOT NULL
                      )
                ) AS invalid_unresolved,

                COUNT(*) FILTER (
                    WHERE classification NOT IN (
                        'EVENT',
                        'COMPLETE_NON_EVENT',
                        'UNRESOLVED'
                    ) OR classification IS NULL
                ) AS unknown_classes

            FROM read_parquet(?)
        """, [str(TARGET_PATH)]).fetchone()

        total, unique, events, non_events, unresolved, unknown = result

        print("\n========== TARGET VALIDATION ==========")
        print(f"Total loans           : {total:,}")
        print(f"Unique loans          : {unique:,}")
        print(f"Invalid events        : {events:,}")
        print(f"Invalid non-events    : {non_events:,}")
        print(f"Invalid unresolved    : {unresolved:,}")
        print(f"Unknown classes       : {unknown:,}")

        if not (
            total == unique == 1_238_192
            and events == 0
            and non_events == 0
            and unresolved == 0
            and unknown == 0
        ):
            raise ValueError("Target validation FAILED")

        print("Final status          : PASSED")

    finally:
        con.close()


if __name__ == "__main__":
    validate_target()
