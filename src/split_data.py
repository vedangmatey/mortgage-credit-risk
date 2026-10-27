
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"

SOURCE = DATA / "modeling_data.parquet"
OUTPUT = DATA / "modeling_split.parquet"
PENDING = DATA / "modeling_split.pending.parquet"

if not SOURCE.exists():
    raise FileNotFoundError(SOURCE)

if OUTPUT.exists() or PENDING.exists():
    raise FileExistsError("Split dataset already exists")

con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")

try:
    con.execute("""
        COPY (
            SELECT
                *,
                CASE
                    WHEN SUBSTR(loan_id, 1, 5)
                         IN ('F07Q1', 'F07Q2')
                        THEN 'TRAIN'

                    WHEN SUBSTR(loan_id, 1, 5) = 'F07Q3'
                        THEN 'VALIDATION'

                    WHEN SUBSTR(loan_id, 1, 5) = 'F07Q4'
                        THEN 'TEST'

                    ELSE 'UNKNOWN'
                END AS data_split

            FROM read_parquet(?)
        )
        TO ?
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """, [str(SOURCE), str(PENDING)])

    results = con.execute("""
        SELECT
            data_split,
            COUNT(*) AS mortgages,
            SUM(target) AS events,
            ROUND(100.0 * AVG(target), 2)
                AS event_rate_pct

        FROM read_parquet(?)
        GROUP BY data_split
        ORDER BY data_split
    """, [str(PENDING)]).fetchall()

    print("========== DATA SPLIT ==========")
    print("Group       | Mortgages | Events | Event Rate")

    for group, loans, events, rate in results:
        print(
            f"{group:<11} | "
            f"{loans:>9,} | "
            f"{events:>6,} | "
            f"{rate:>6.2f}%"
        )

    assert sum(r[1] for r in results) == 888_123
    assert sum(r[2] for r in results) == 59_785
    assert {r[0] for r in results} == {
        "TRAIN", "VALIDATION", "TEST"
    }

    assert all(
        0 < events < loans
        for _, loans, events, _ in results
    )

    PENDING.rename(OUTPUT)

    print("\nData splitting: PASSED")
    print(f"Output: {OUTPUT}")

finally:
    con.close()
