
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"

ORIG = (DATA / "orig_2007Q*.parquet").as_posix()
TARGET = (DATA / "target_preliminary.parquet").as_posix()
OUTPUT = DATA / "modeling_data.parquet"
PENDING = DATA / "modeling_data.pending.parquet"

if OUTPUT.exists() or PENDING.exists():
    raise FileExistsError("Modeling output already exists")

con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")
con.execute("SET temp_directory='data/temp'")

try:
    con.execute(f"""
        COPY (
            SELECT
                o.column19 AS loan_id,
                t.first_payment_date,
                t.target,

                CASE
                    WHEN TRY_CAST(o.column00 AS DOUBLE)
                        BETWEEN 300 AND 850
                    THEN TRY_CAST(o.column00 AS DOUBLE)
                END AS credit_score,

                CASE
                    WHEN TRY_CAST(o.column11 AS DOUBLE)
                        BETWEEN 1 AND 105
                    THEN TRY_CAST(o.column11 AS DOUBLE)
                END AS original_ltv,

                CASE
                    WHEN TRY_CAST(o.column08 AS DOUBLE)
                        BETWEEN 1 AND 200
                    THEN TRY_CAST(o.column08 AS DOUBLE)
                END AS original_cltv,

                CASE
                    WHEN TRY_CAST(o.column09 AS DOUBLE)
                        BETWEEN 1 AND 65
                    THEN TRY_CAST(o.column09 AS DOUBLE)
                END AS original_dti,

                CASE
                    WHEN TRY_CAST(o.column12 AS DOUBLE) > 0
                    THEN TRY_CAST(o.column12 AS DOUBLE)
                END AS interest_rate,

                CASE
                    WHEN TRY_CAST(o.column10 AS DOUBLE) > 0
                    THEN TRY_CAST(o.column10 AS DOUBLE)
                END AS loan_amount

            FROM read_parquet('{ORIG}') o
            JOIN read_parquet('{TARGET}') t
                ON o.column19 = t.loan_id

            WHERE t.target IS NOT NULL
        )
        TO '{PENDING.as_posix()}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    total, unique, events, non_events = con.execute("""
        SELECT
            COUNT(*),
            COUNT(DISTINCT loan_id),
            COUNT(*) FILTER (WHERE target = 1),
            COUNT(*) FILTER (WHERE target = 0)
        FROM read_parquet(?)
    """, [str(PENDING)]).fetchone()

    print("========== MODELING DATA ==========")
    print(f"Total mortgages : {total:,}")
    print(f"Unique mortgages: {unique:,}")
    print(f"Events          : {events:,}")
    print(f"Non-events      : {non_events:,}")
    print("Predictive features: 6")

    assert (total, unique, events, non_events) == (
        888_123, 888_123, 59_785, 828_338
    )

    PENDING.rename(OUTPUT)

    print(f"\nOutput: {OUTPUT}")
    print("Validation: PASSED")

finally:
    con.close()
