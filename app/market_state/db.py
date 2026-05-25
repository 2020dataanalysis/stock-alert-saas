import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

MARKET_STATE_DB_PATH = (
    BASE_DIR / "data" / "market_state.db"
)


def get_connection():

    conn = sqlite3.connect(
        MARKET_STATE_DB_PATH
    )

    conn.execute(
        "PRAGMA journal_mode=WAL;"
    )

    conn.execute(
        "PRAGMA busy_timeout=30000;"
    )

    return conn


def init_db():

    MARKET_STATE_DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_state_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                event_type TEXT NOT NULL,
                price REAL,
                velocity_pct REAL,
                confidence_score REAL,
                message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_state_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL,
                shock_score REAL,
                trend_score REAL,
                noise_score REAL,
                state TEXT,
                trade_permission TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_state_events_symbol_timestamp
            ON market_state_events(symbol, timestamp)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_state_snapshots_symbol_timestamp
            ON market_state_snapshots(symbol, timestamp)
        """)

        conn.commit()


if __name__ == "__main__":

    init_db()

    print(
        f"Initialized DB: "
        f"{MARKET_STATE_DB_PATH}"
    )
