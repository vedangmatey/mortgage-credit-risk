
from pathlib import Path
import duckdb

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Local database paths
DATA_DIR = PROJECT_ROOT / "data"
TEMP_DIR = DATA_DIR / "temp"
DB_PATH = DATA_DIR / "mortgage.duckdb"

# Create directories if they do not exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Create an optimized DuckDB connection for an 8 GB RAM laptop."""

    con = duckdb.connect(str(DB_PATH))

    # Conservative settings for local development
    con.execute("SET memory_limit = '3GB'")
    con.execute("SET threads = 2")
    con.execute(
        "SET temp_directory = ?",
        [str(TEMP_DIR)]
    )

    return con
