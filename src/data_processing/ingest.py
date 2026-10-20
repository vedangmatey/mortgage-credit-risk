
"""
Freddie Mac Mortgage Origination Data Ingestion

Features:
- Supports all four quarters of 2007
- Uses DuckDB for efficient processing
- Converts raw text files to compressed Parquet
- Preserves raw values as strings
- Validates output
- Prevents accidental overwriting
- Cleans up temporary extracted files
"""

import argparse
import shutil
import time
from zipfile import ZipFile

from config.database import get_connection, PROJECT_ROOT
from config.schema import ORIGINATION_COLUMNS, DELIMITER


RAW_ZIP = PROJECT_ROOT / "data/raw/historical_data_2007.zip"
TEMP_DIR = PROJECT_ROOT / "data/temp"
OUTPUT_DIR = PROJECT_ROOT / "data/processed/origination"

VALID_QUARTERS = [
    "2007Q1",
    "2007Q2",
    "2007Q3",
    "2007Q4",
]


def ingest_origination(quarter: str):

    if quarter not in VALID_QUARTERS:
        raise ValueError(f"Invalid quarter: {quarter}")

    start = time.perf_counter()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    quarterly_zip = TEMP_DIR / f"historical_data_{quarter}.zip"
    raw_txt = TEMP_DIR / f"orig_{quarter}.txt"
    output_file = OUTPUT_DIR / f"origination_{quarter}.parquet"
    pending_file = OUTPUT_DIR / f"origination_{quarter}.pending.parquet"

    if not RAW_ZIP.is_file():
        raise FileNotFoundError(RAW_ZIP)

    if output_file.exists():
        raise FileExistsError(
            f"Output already exists: {output_file}"
        )

    con = None

    try:
        # STEP 1: Extract quarterly ZIP
        print(f"\nProcessing {quarter}", flush=True)
        print("Extracting quarterly archive...", flush=True)

        with ZipFile(RAW_ZIP) as outer:
            with outer.open(quarterly_zip.name) as source:
                with quarterly_zip.open("wb") as target:
                    shutil.copyfileobj(source, target)

        # STEP 2: Extract origination TXT
        print("Extracting origination file...", flush=True)

        with ZipFile(quarterly_zip) as inner:
            with inner.open(raw_txt.name) as source:
                with raw_txt.open("wb") as target:
                    shutil.copyfileobj(source, target)

        # STEP 3: Connect to DuckDB
        print("Connecting to DuckDB...", flush=True)

        con = get_connection()

        columns = ", ".join(
            f"'col_{i:02d}': 'VARCHAR'"
            for i in range(1, len(ORIGINATION_COLUMNS) + 1)
        )

        source_path = raw_txt.as_posix().replace("'", "''")
        destination_path = pending_file.as_posix().replace("'", "''")

        # STEP 4: Convert to Parquet
        print("Converting to Parquet...", flush=True)

        con.execute(f"""
            COPY (
                SELECT *
                FROM read_csv(
                    '{source_path}',
                    delim = '{DELIMITER}',
                    header = false,
                    auto_detect = false,
                    columns = {{{columns}}},
                    quote = ''
                )
            )
            TO '{destination_path}'
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        # STEP 5: Validate output
        print("Validating data...", flush=True)

        result = con.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (
                    WHERE col_20 IS NULL
                       OR TRIM(col_20) = ''
                ) AS missing_loan_ids,
                COUNT(DISTINCT col_20) AS unique_loans
            FROM read_parquet(?)
        """, [str(pending_file)]).fetchone()

        total_rows, missing_ids, unique_loans = result

        column_count = len(
            con.execute(
                "DESCRIBE SELECT * FROM read_parquet(?)",
                [str(pending_file)]
            ).fetchall()
        )

        if total_rows == 0:
            raise ValueError("Origination file is empty")

        if column_count != len(ORIGINATION_COLUMNS):
            raise ValueError("Incorrect column count")

        if missing_ids != 0:
            raise ValueError("Missing Loan Sequence Numbers")

        if unique_loans != total_rows:
            raise ValueError("Duplicate Loan Sequence Numbers detected")

        con.close()
        con = None

        # STEP 6: Publish validated output
        pending_file.replace(output_file)

        elapsed = time.perf_counter() - start

        print("\n========== ORIGINATION INGESTION ==========")
        print(f"Quarter               : {quarter}")
        print(f"Total mortgage records: {total_rows:,}")
        print(f"Unique loans          : {unique_loans:,}")
        print(f"Columns               : {column_count}")
        print(f"Missing loan IDs      : {missing_ids:,}")
        print(f"Parquet size (MB)     : {output_file.stat().st_size / 1024**2:.2f}")
        print(f"Processing time (sec) : {elapsed:.2f}")
        print(f"Output                : {output_file}")
        print("Validation            : PASSED")

    finally:
        if con is not None:
            con.close()

        raw_txt.unlink(missing_ok=True)
        quarterly_zip.unlink(missing_ok=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Freddie Mac Origination Data Ingestion"
    )

    parser.add_argument(
        "--quarter",
        required=True,
        choices=VALID_QUARTERS,
        help="Quarter to process"
    )

    args = parser.parse_args()

    ingest_origination(args.quarter)
