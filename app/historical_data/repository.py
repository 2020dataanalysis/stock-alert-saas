from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]

HISTORICAL_DB_PATH = (
    BASE_DIR / "data" / "historical_data.db"
)


def get_historical_connection():
    HISTORICAL_DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(
        HISTORICAL_DB_PATH
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_historical_db():
    with get_historical_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS opening_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                gap_pct REAL,
                open_price REAL,
                previous_close REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS minute_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER NOT NULL,
                minute_number INTEGER NOT NULL,
                price REAL,
                distance_from_open_pct REAL,
                broke_below_open INTEGER,
                broke_above_open INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id)
                    REFERENCES opening_scenarios(id)
            )
        """)

        conn.commit()
