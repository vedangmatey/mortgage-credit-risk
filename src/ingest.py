
from pathlib import Path
import zipfile
import shutil
import duckdb


# ---------------------------------------
# 1. Project paths
# ---------------------------------------

ROOT = Path(__file__).resolve().parent.parent

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
TEMP = ROOT / "data" / "temp"

ZIP_FILE = RAW / "historical_data_2007.zip"

PROCESSED.mkdir(parents=True, exist_ok=True)
TEMP.mkdir(parents=True, exist_ok=True)


# ---------------------------------------
# 2. Expected record counts
# ---------------------------------------

EXPECTED = {
    "2007Q1": {"orig": 302331, "perf": 19432995},
    "2007Q2": {"orig": 354055, "perf": 22286961},
    "2007Q3": {"orig": 284980, "perf": 15827144},
    "2007Q4": {"orig": 296826, "perf": 16931624},
}

COLUMNS = {"orig": 31, "perf": 35}


# ---------------------------------------
# 3. DuckDB connection
# ---------------------------------------

con = duckdb.connect()

con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")


def sql_path(path):
    return path.as_posix().replace("'", "''")


# ---------------------------------------
# 4. Validate Parquet data
# ---------------------------------------

def validate(path, quarter, kind):

    result = con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{sql_path(path)}')
    """).fetchone()[0]

    columns = len(con.execute(f"""
        SELECT *
        FROM read_parquet('{sql_path(path)}')
        LIMIT 0
    """).description)

    expected_rows = EXPECTED[quarter][kind]
    expected_columns = COLUMNS[kind]

    if result != expected_rows or columns != expected_columns:
        raise ValueError(
            f"Validation failed: {quarter} {kind}. "
            f"Found {result:,} rows and {columns} columns."
        )

    print(f"  Records: {result:,}")
    print(f"  Columns: {columns}")
    print("  Validation: PASSED")


# ---------------------------------------
# 5. Convert one text file
# ---------------------------------------

def convert(inner_zip, quarter, kind):

    output = PROCESSED / f"{kind}_{quarter}.parquet"

    print(f"\n{quarter} | {kind.upper()}")

    # Skip previously validated output
    if output.exists():
        validate(output, quarter, kind)
        print("  Already processed — SKIPPED")
        return

    text_name = f"{kind}_{quarter}.txt"
    text_path = TEMP / text_name

    pending = PROCESSED / f"{kind}_{quarter}.pending.parquet"

    if pending.exists():
        raise FileExistsError(
            f"Incomplete prior output found: {pending}"
        )

    try:
        # Extract the text file temporarily
        with inner_zip.open(text_name) as source:
            with text_path.open("wb") as destination:
                shutil.copyfileobj(source, destination)

        # Convert text to Parquet
        con.execute(f"""
            COPY (
                SELECT *
                FROM read_csv(
                    '{sql_path(text_path)}',
                    delim='|',
                    header=false,
                    all_varchar=true
                )
            )
            TO '{sql_path(pending)}'
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        # Validate before finalizing the output
        validate(pending, quarter, kind)

        pending.rename(output)
        print(f"  Saved: {output.name}")

    finally:
        text_path.unlink(missing_ok=True)


# ---------------------------------------
# 6. Process all four quarters
# ---------------------------------------

def main():

    if not ZIP_FILE.is_file():
        raise FileNotFoundError(ZIP_FILE)

    try:
        with zipfile.ZipFile(ZIP_FILE) as outer:

            for quarter in EXPECTED:

                print(f"\n========== {quarter} ==========")

                outer_name = f"historical_data_{quarter}.zip"
                temp_zip = TEMP / outer_name

                orig_output = PROCESSED / f"orig_{quarter}.parquet"
                perf_output = PROCESSED / f"perf_{quarter}.parquet"

                # No need to extract if both already exist
                if orig_output.exists() and perf_output.exists():
                    validate(orig_output, quarter, "orig")
                    validate(perf_output, quarter, "perf")
                    print("Quarter already complete — SKIPPED")
                    continue

                try:
                    # Extract quarterly ZIP
                    with outer.open(outer_name) as source:
                        with temp_zip.open("wb") as destination:
                            shutil.copyfileobj(source, destination)

                    # Process both files inside the quarter
                    with zipfile.ZipFile(temp_zip) as inner:
                        convert(inner, quarter, "orig")
                        convert(inner, quarter, "perf")

                finally:
                    temp_zip.unlink(missing_ok=True)

        print("\n========== INGESTION COMPLETE ==========")

        total_orig = sum(v["orig"] for v in EXPECTED.values())
        total_perf = sum(v["perf"] for v in EXPECTED.values())

        print(f"Total mortgages: {total_orig:,}")
        print(f"Monthly records: {total_perf:,}")
        print("All quarterly validations: PASSED")

    finally:
        con.close()


if __name__ == "__main__":
    main()
