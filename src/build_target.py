
from pathlib import Path
import duckdb

# Project locations
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"

ORIG = (DATA / "orig_2007Q*.parquet").as_posix()
PERF = (DATA / "perf_2007Q*.parquet").as_posix()
OUTPUT = DATA / "target_events.parquet"

# Connect to DuckDB
con = duckdb.connect()

con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")
con.execute("SET temp_directory='data/temp'")

# Identify mortgages with serious delinquency
con.execute("""
    COPY (
        WITH origination AS (
            SELECT
                column19 AS loan_id,
                column01 AS first_payment_date
            FROM read_parquet(?)
        ),

        events AS (
            SELECT DISTINCT
                p.column00 AS loan_id

            FROM read_parquet(?) p

            JOIN origination o
                ON p.column00 = o.loan_id

            WHERE TRY_CAST(p.column03 AS INTEGER)
                  BETWEEN 3 AND 98

              AND (
                  TRY_CAST(SUBSTR(p.column01, 1, 4) AS INTEGER) * 12
                  + TRY_CAST(SUBSTR(p.column01, 5, 2) AS INTEGER)
                  - TRY_CAST(SUBSTR(o.first_payment_date, 1, 4) AS INTEGER) * 12
                  - TRY_CAST(SUBSTR(o.first_payment_date, 5, 2) AS INTEGER)
              ) BETWEEN 0 AND 23
        )

        SELECT
            o.loan_id,
            o.first_payment_date,

            CASE
                WHEN e.loan_id IS NOT NULL THEN 1
                ELSE 0
            END AS observed_serious_event

        FROM origination o
        LEFT JOIN events e
            ON o.loan_id = e.loan_id
    )
    TO ?
    (FORMAT PARQUET, COMPRESSION ZSTD)
""", [ORIG, PERF, str(OUTPUT)])

# Validate the output
result = con.execute("""
    SELECT
        COUNT(*),
        COUNT(DISTINCT loan_id),
        SUM(observed_serious_event)
    FROM read_parquet(?)
""", [str(OUTPUT)]).fetchone()

print("Total mortgages :", f"{result[0]:,}")
print("Unique mortgages:", f"{result[1]:,}")
print("Observed events :", f"{result[2]:,}")

assert result == (1_238_192, 1_238_192, 59_785)

print("\nTarget event validation: PASSED")

con.close()
