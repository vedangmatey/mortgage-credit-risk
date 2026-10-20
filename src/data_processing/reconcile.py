
"""Reconcile mortgage origination and performance data."""

import argparse
import time

from config.database import get_connection, PROJECT_ROOT


def reconcile(quarter: str):
    start = time.perf_counter()

    orig = (
        PROJECT_ROOT / "data/processed/origination"
        / f"origination_{quarter}.parquet"
    )
    perf = (
        PROJECT_ROOT / "data/processed/performance"
        / f"performance_{quarter}.parquet"
    )

    for path in (orig, perf):
        if not path.is_file():
            raise FileNotFoundError(path)

    con = get_connection()

    try:
        # Parameterized SELECT queries avoid path interpolation.
        con.execute("""
            CREATE TEMP TABLE orig_ids AS
            SELECT col_20 AS loan_id
            FROM read_parquet(?)
        """, [str(orig)])

        con.execute("""
            CREATE TEMP TABLE perf_summary AS
            SELECT
                col_01 AS loan_id,
                COUNT(*) AS monthly_records,
                COUNT(DISTINCT col_02) AS unique_months
            FROM read_parquet(?)
            GROUP BY col_01
        """, [str(perf)])

        result = con.execute("""
            SELECT
                COUNT(*) AS performance_loans,
                COUNT(*) FILTER (
                    WHERE o.loan_id IS NOT NULL
                ) AS matched_loans,
                COUNT(*) FILTER (
                    WHERE o.loan_id IS NULL
                ) AS unmatched_performance_loans,
                COALESCE(
                    SUM(p.monthly_records - p.unique_months), 0
                ) AS duplicate_loan_months
            FROM perf_summary p
            LEFT JOIN orig_ids o
                ON p.loan_id = o.loan_id
        """).fetchone()

        missing_orig = con.execute("""
            SELECT COUNT(*)
            FROM orig_ids o
            LEFT JOIN perf_summary p
                ON o.loan_id = p.loan_id
            WHERE p.loan_id IS NULL
        """).fetchone()[0]

        total, matched, unmatched, duplicates = result

        print(f"\n========== {quarter} RECONCILIATION ==========")
        print(f"Performance loans        : {total:,}")
        print(f"Matched loans            : {matched:,}")
        print(f"Unmatched performance    : {unmatched:,}")
        print(f"Origination without perf : {missing_orig:,}")
        print(f"Duplicate loan-months    : {duplicates:,}")
        print(f"Execution time (sec)     : {time.perf_counter() - start:.2f}")

        passed = (
            unmatched == 0
            and missing_orig == 0
            and duplicates == 0
            and matched == total
        )

        print(f"Validation               : {'PASSED' if passed else 'FAILED'}")

        if not passed:
            raise ValueError("Cross-file reconciliation failed")

    finally:
        con.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quarter", default="2007Q1")
    args = parser.parse_args()

    reconcile(args.quarter)
