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
                range_pct REAL,
                transition_type TEXT,
                priority TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS scalp_state_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                state TEXT NOT NULL,
                previous_state TEXT,
                action TEXT,
                score INTEGER,
                latest REAL,
                range_pct REAL,
                range_velocity REAL,
                older_range_pct REAL,
                recent_range_pct REAL,
                directional_efficiency REAL,
                compression_maturity_score INTEGER,
                compression_label TEXT,
                expansion_exhaustion_score INTEGER,
                expansion_exhaustion_label TEXT,
                volume_samples INTEGER,
                volume_delta REAL,
                volume_delta_per_sample REAL,
                volume_efficiency REAL,
                relative_volume_ratio REAL,
                relative_volume_label TEXT,
                reason TEXT,
                event_type TEXT
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_scalp_state_log_symbol_id
            ON scalp_state_log(symbol, id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_scalp_state_log_timestamp
            ON scalp_state_log(timestamp)
        """)
