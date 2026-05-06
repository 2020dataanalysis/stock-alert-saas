import sqlite3
from pathlib import Path

DB_PATH = Path("data/market_data.db")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                bid REAL,
                ask REAL,
                last REAL,
                last_size INTEGER,
                volume INTEGER,
                is_shortable INTEGER,
                hard_to_borrow INTEGER,
                htb_rate REAL
            )
        """)


def save_quote(quote):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO quotes (
                timestamp,
                symbol,
                bid,
                ask,
                last,
                last_size,
                volume,
                is_shortable,
                hard_to_borrow,
                htb_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quote["timestamp"],
            quote["symbol"],
            quote.get("bid"),
            quote.get("ask"),
            quote.get("last"),
            quote.get("last_size"),
            quote.get("volume"),
            int(quote.get("is_shortable", False)),
            int(quote.get("hard_to_borrow", False)),
            quote.get("htb_rate"),
        ))