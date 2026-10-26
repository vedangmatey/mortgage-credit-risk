
import duckdb

con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")

file = "data/processed/orig_2007Q*.parquet"

result = con.execute("""
    SELECT
        COUNT(*) AS total_mortgages,
        COUNT(DISTINCT column19) AS unique_mortgages,
        COUNT(*) - COUNT(DISTINCT column19) AS difference,
        COUNT(*) FILTER (
            WHERE column19 IS NULL OR TRIM(column19) = ''
        ) AS missing_ids
    FROM read_parquet(?)
""", [file]).fetchone()

print("Total mortgages :", f"{result[0]:,}")
print("Unique mortgages:", f"{result[1]:,}")
print("Difference      :", f"{result[2]:,}")
print("Missing IDs     :", f"{result[3]:,}")

assert result == (1238192, 1238192, 0, 0)

print("\nValidation: PASSED")


# Step 49 — Check performance loan IDs against origination

print("\nChecking performance loan IDs...")

result = con.execute("""
    WITH perf_loans AS (
        SELECT DISTINCT column00 AS loan_id
        FROM read_parquet(?)
    ),
    orig_loans AS (
        SELECT column19 AS loan_id
        FROM read_parquet(?)
    )
    SELECT
        COUNT(*) AS performance_loans,

        COUNT(*) FILTER (
            WHERE o.loan_id IS NULL
        ) AS unmatched_loans,

        COUNT(*) FILTER (
            WHERE p.loan_id IS NULL
               OR TRIM(p.loan_id) = ''
        ) AS missing_ids

    FROM perf_loans p
    LEFT JOIN orig_loans o
        ON p.loan_id = o.loan_id
""", [
    "data/processed/perf_2007Q*.parquet",
    "data/processed/orig_2007Q*.parquet"
]).fetchone()

print(f"Performance loan IDs : {result[0]:,}")
print(f"Unmatched loan IDs   : {result[1]:,}")
print(f"Missing loan IDs     : {result[2]:,}")

assert result == (1238192, 0, 0)

print("Performance ID validation: PASSED")


# Step 50 — Validate monthly reporting dates

print("\nChecking monthly reporting dates...")

result = con.execute("""
    SELECT
        COUNT(*) AS total_records,

        COUNT(*) FILTER (
            WHERE column01 IS NULL
               OR NOT regexp_full_match(column01, '[0-9]{6}')
               OR TRY_CAST(SUBSTR(column01, 5, 2) AS INTEGER)
                  NOT BETWEEN 1 AND 12
        ) AS invalid_dates

    FROM read_parquet(?)
""", ["data/processed/perf_2007Q*.parquet"]).fetchone()

print(f"Total monthly records : {result[0]:,}")
print(f"Invalid reporting dates: {result[1]:,}")

assert result[0] == 74_478_724
assert result[1] == 0

print("Reporting date validation: PASSED")


# Step 51 — Check duplicate loan-month combinations

print("\nChecking duplicate monthly records...")

con.execute("SET temp_directory='data/temp'")

for quarter in ["2007Q1", "2007Q2", "2007Q3", "2007Q4"]:

    file = f"data/processed/perf_{quarter}.parquet"

    duplicate = con.execute("""
        SELECT
            column00 AS loan_id,
            column01 AS reporting_month,
            COUNT(*) AS occurrences
        FROM read_parquet(?)
        GROUP BY column00, column01
        HAVING COUNT(*) > 1
        LIMIT 1
    """, [file]).fetchone()

    if duplicate:
        raise ValueError(
            f"Duplicate found in {quarter}: {duplicate}"
        )

    print(f"{quarter}: No duplicate loan-month records")

print("\nMonthly uniqueness validation: PASSED")


con.close()
