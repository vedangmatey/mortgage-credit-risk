
"""
Freddie Mac mortgage data ingestion.
Phase 1: Process Q1 2007 origination records.
"""

from pathlib import Path
from zipfile import ZipFile
import shutil
import time

from config.database import get_connection, PROJECT_ROOT
from config.schema import ORIGINATION_COLUMNS, DELIMITER


RAW_ZIP = PROJECT_ROOT / "data/raw/historical_data_2007.zip"
TEMP_DIR = PROJECT_ROOT / "data/temp"
OUTPUT_DIR = PROJECT_ROOT / "data/processed/origination"

QUARTER = "2007Q1"


def ingest_origination():

    start = time.perf_counter()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    quarterly_zip = TEMP_DIR / f"historical_data_{QUARTER}.zip"
    raw_txt = TEMP_DIR / f"orig_{QUARTER}.txt"
    output_file = OUTPUT_DIR / f"origination_{QUARTER}.parquet"

    if not RAW_ZIP.is_file():
        raise FileNotFoundError(RAW_ZIP)

    # Prevent accidental replacement of existing output
    if output_file.exists():
        raise FileExistsError(
            f"Output already exists: {output_file}"
        )

    con = None

    try:
        print("Extracting quarterly archive...")

        with ZipFile(RAW_ZIP) as outer:
            with outer.open(quarterly_zip.name) as source:
                with quarterly_zip.open("wb") as target:
                    shutil.copyfileobj(source, target)

        print("Extracting origination file...")

        with ZipFile(quarterly_zip) as inner:
            with inner.open(raw_txt.name) as source:
                with raw_txt.open("wb") as target:
                    shutil.copyfileobj(source, target)

        print("Connecting to DuckDB...")

        con = get_connection()

        # Preserve original source values as VARCHAR
        column_definitions = ", ".join(
            f"'col_{i:02d}': 'VARCHAR'"
            for i in range(1, len(ORIGINATION_COLUMNS) + 1)
        )

        source_path = raw_txt.as_posix().replace("'", "''")
        destination_path = output_file.as_posix().replace("'", "''")

        print("Converting to Parquet...")

        con.execute(f"""
            COPY (
                SELECT *
                FROM read_csv(
                    '{source_path}',
                    delim = '{DELIMITER}',
                    header = false,
                    auto_detect = false,
                    columns = {{{column_definitions}}},
                    quote = ''
                )
            )
            TO '{destination_path}'
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """)

        row_count = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)",
            [str(output_file)]
        ).fetchone()[0]

        column_count = len(
            con.execute(
                "DESCRIBE SELECT * FROM read_parquet(?)",
                [str(output_file)]
            ).fetchall()
        )

        assert column_count == len(ORIGINATION_COLUMNS)
        assert row_count > 0

        elapsed = time.perf_counter() - start

        print("\n========== INGESTION SUMMARY ==========")
        print(f"Quarter: {QUARTER}")
        print(f"Rows: {row_count:,}")
        print(f"Columns: {column_count}")
        print(f"Output: {output_file}")
        print(f"Output MB: {output_file.stat().st_size / 1024**2:.2f}")
        print(f"Processing time: {elapsed:.2f} seconds")
        print("Validation: PASSED")

    finally:
        if con is not None:
            con.close()

        # Remove temporary extracted files
        raw_txt.unlink(missing_ok=True)
        quarterly_zip.unlink(missing_ok=True)


if __name__ == "__main__":
    ingest_origination()
