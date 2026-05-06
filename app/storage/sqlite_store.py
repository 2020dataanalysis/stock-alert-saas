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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                type TEXT,
                price_change_pct REAL,
                volume_change_pct REAL,
                oldest_price REAL,
                newest_price REAL,
                oldest_volume REAL,
                newest_volume REAL
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


def save_alert(alert):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO alerts (
                timestamp,
                symbol,
                type,
                price_change_pct,
                volume_change_pct,
                oldest_price,
                newest_price,
                oldest_volume,
                newest_volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.get("timestamp"),
            alert.get("symbol"),
            alert.get("type"),
            alert.get("price_change_pct"),
            alert.get("volume_change_pct"),
            alert.get("oldest_price"),
            alert.get("newest_price"),
            alert.get("oldest_volume"),
            alert.get("newest_volume"),
        ))