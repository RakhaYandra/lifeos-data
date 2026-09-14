"""Extract: baca 8 tabel inti dari snapshot SQLite (read-only)."""
import sqlite3
from pathlib import Path

TABLES = ["tasks", "projects", "goals", "habits", "habit_logs",
          "transactions", "budgets", "health_logs", "workouts"]

ROOT = Path(__file__).resolve().parent


def snapshot_db() -> Path:
    """Lokasi snapshot. Env LIFEOS_DB untuk analisis pribadi (tak di-commit)."""
    import os
    return Path(os.environ.get("LIFEOS_DB", ROOT / "work" / "seed.db"))


def extract(db_path: Path | None = None) -> dict:
    db = db_path or snapshot_db()
    if not db.exists():
        raise SystemExit(f"snapshot tak ada: {db} (jalankan run.sh dulu)")
    uri = f"file:{db}?mode=ro"
    out = {}
    con = sqlite3.connect(uri, uri=True)
    try:
        import pandas as pd
        for t in TABLES:
            out[t] = pd.read_sql_query(f"SELECT * FROM {t}", con)
    finally:
        con.close()
    return out
