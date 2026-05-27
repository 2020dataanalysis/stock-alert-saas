from pathlib import Path
import sqlite3
from contextlib import contextmanager


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SCALP_STATE_DB_PATH = DATA_DIR / "scalp_state.db"


@contextmanager
def scalp_state_db_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(SCALP_STATE_DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_scalp_state_db():
    with scalp_state_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scalp_state_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                previous_state TEXT,
                current_state TEXT NOT NULL,
                duration_seconds INTEGER,
                score INTEGER,
                range_pct REAL
            )
        """)
