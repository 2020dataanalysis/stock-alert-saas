from __future__ import annotations

from pathlib import Path
import sqlite3


DB_PATH = Path("data/gap_data.db")


def get_gap_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")

    return conn


def initialize_gap_database():
    with get_gap_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS gap_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT NOT NULL,
                trade_date TEXT NOT NULL,

                detected_at TEXT NOT NULL,

                gap_pct REAL NOT NULL,
                gap_direction TEXT NOT NULL,

                previous_close REAL,
                open_price REAL,
                last_price REAL,

                volume INTEGER,

                is_shortable INTEGER,
                hard_to_borrow INTEGER,

                source TEXT,

                created_at TEXT NOT NULL,

                UNIQUE(symbol, trade_date)
            )
            """
        )

    return {
        "database": str(DB_PATH),
        "initialized": True,
    }
