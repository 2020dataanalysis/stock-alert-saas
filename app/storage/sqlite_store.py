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


        conn.execute("""
            CREATE TABLE IF NOT EXISTS provider_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                provider TEXT NOT NULL,
                symbol TEXT,
                operation TEXT,
                error_type TEXT,
                message TEXT,
                raw_response TEXT
            )
        """)


    init_streamer_control_table()


def init_streamer_control_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS streamer_control (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        mode TEXT,
        until_timestamp TEXT
    )
    """)

    # ensure single row exists
    cur.execute("SELECT COUNT(*) FROM streamer_control")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO streamer_control (id, mode, until_timestamp)
        VALUES (1, 'auto', NULL)
        """)

    conn.commit()
    conn.close()




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
            quote.get("timestamp") or datetime.now(timezone.utc).isoformat(),
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


def get_top_movers(limit=5):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT
                symbol,
                type,
                price_change_pct,
                volume_change_pct,
                timestamp
            FROM alerts
            WHERE price_change_pct IS NOT NULL
            ORDER BY ABS(price_change_pct) DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()



def save_provider_error(
    provider,
    symbol=None,
    operation=None,
    error_type=None,
    message=None,
    raw_response=None,
):
    from datetime import datetime, UTC
    import json

    if raw_response is not None and not isinstance(raw_response, str):
        raw_response = json.dumps(raw_response, default=str)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO provider_errors (
                timestamp,
                provider,
                symbol,
                operation,
                error_type,
                message,
                raw_response
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(UTC).isoformat(),
            provider,
            symbol,
            operation,
            error_type,
            message,
            raw_response,
        ))