"""Run every query in sql/ against the SQLite database and save each result to outputs/.

Run from the repository root (after src/clean_data.py):  python src/run_queries.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)
pd.set_option("display.width", 160)
pd.set_option("display.max_colwidth", 70)

with sqlite3.connect("data/restaurant_inspections.db") as con:
    con.execute("CREATE INDEX IF NOT EXISTS idx_insp ON inspections (restaurant_id, inspection_type, inspection_date)")
    for path in sorted(Path("sql").glob("*.sql")):
        result = pd.read_sql_query(path.read_text(), con)
        result.to_csv(OUT / f"{path.stem}.csv", index=False)
        print(f"\n=== {path.stem} ===")
        print(result.to_string(index=False))
