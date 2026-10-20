
"""
Freddie Mac monthly performance data ingestion.
Phase 1: 2007 Q1.

Processes large files using DuckDB without pandas.
"""

from pathlib import Path
from zipfile import ZipFile
import shutil
import time

from config.database import get_connection, PROJECT_ROOT
from config.schema import PERFORMANCE_COLUMNS


QUARTER = "2007Q1"

RAW_ZIP = PROJECT_ROOT / "data/raw/historical_data_2007.zip"
TEMP_DIR = PROJECT_ROOT / "data/temp"
OUTPUT_DIR = PROJECT_ROOT / "data/processed/performance"


def ingest_performance():

    start = time.perf_counter()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    quarterly_zip = TEMP_DIR / f"historical_data_{QUARTER}.zip"
    raw_txt = TEMP_DIR / f"perf_{QUARTER}.txt"
    output_file = OUTPUT_DIR / f"performance_{QUARTER}.parquet"
    pending_file = OUTPUT_DIR / f"performance_{QUARTER}.pending.parquet"

    if not RAW_ZIP.exists():
        raise FileNotFoundError(RAW_ZIP)

    if output_file.exists():
        raise FileExistsError(f"Output already exists: {output_file}")

    con = None

    try:
        # Step 1: Extract quarter ZIP
        print("Extracting quarterly archive...", flush=True)

        with ZipFile(RAW_ZIP) as outer:
            with outer.open(quarterly_zip.name) as source:
                with quarterly_zip.open("wb") as target:
                    shutil.copyfileobj(source, target)

        # Step 2: Extract performance data
        print("Extracting performance file...", flush=True)

        with ZipFile(quarterly_zip) as inner:
            with inner.open(raw_txt.name) as source:
                with raw_txt.open("wb") as target:
                    shutil.copyfileobj(source, target)

        # Step 3: Connect DuckDB
        con = get_connection()

        columns = ", ".join(
            f"'col_{i:02d}': 'VARCHAR'"
            for i in range(1, len(PERFORMANCE_COLUMNS) + 1)
        )

        source_path = raw_txt.as_posix().replace("'", "''")
        target_path = pending_file.as_posix().replace("'", "''")

        # Step 4: Convert to Parquet
        print("Converting performance data to Parquet...", flush=True)

        con.execute(f"""
            COPY (
                SELECT *
                FROM read_csv(
                    '{source_path}',
                    delim = '|',
                    header = false,
                    auto_detect = false,
                    columns = {{{columns}}},
                    quote = ''
                )
            )
            TO '{target_path}'
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        # Step 5: Validate output
        print("Validating output...", flush=True)

        result = con.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (
                    WHERE col_01 IS NULL
                       OR TRIM(col_01) = ''
                ) AS missing_loan_ids,
                COUNT(*) FILTER (
                    WHERE col_02 IS NULL
                       OR TRIM(col_02) = ''
                ) AS missing_reporting_periods
            FROM read_parquet(?)
        """, [str(pending_file)]).fetchone()

        total_rows, missing_ids, missing_periods = result

        column_count = len(
            con.execute(
                "DESCRIBE SELECT * FROM read_parquet(?)",
                [str(pending_file)]
            ).fetchall()
        )

        if total_rows == 0:
            raise ValueError("Performance file is empty")

        if column_count != 35:
            raise ValueError("Incorrect number of columns")

        if missing_ids != 0:
            raise ValueError("Missing loan identifiers detected")

        if missing_periods != 0:
            raise ValueError("Missing reporting periods detected")

        con.close()
        con = None

        # Publish only after successful validation
        pending_file.rename(output_file)

        elapsed = time.perf_counter() - start

        print("\n========== PERFORMANCE INGESTION ==========")
        print(f"Quarter              : {QUARTER}")
        print(f"Total monthly records: {total_rows:,}")
        print(f"Columns              : {column_count}")
        print(f"Missing loan IDs     : {missing_ids:,}")
        print(f"Missing report dates : {missing_periods:,}")
        print(f"Parquet size (MB)    : {output_file.stat().st_size / 1024**2:.2f}")
        print(f"Processing time (sec): {elapsed:.2f}")
        print(f"Output               : {output_file}")
        print("Validation           : PASSED")

    finally:
        if con is not None:
            con.close()

        raw_txt.unlink(missing_ok=True)
        quarterly_zip.unlink(missing_ok=True)


if __name__ == "__main__":
    ingest_performance()
