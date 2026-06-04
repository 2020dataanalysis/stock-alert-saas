# stock-alert-saas/app/storage/sqlite_store.py


from datetime import datetime, UTC
import json
import sqlite3
from pathlib import Path
from threading import Lock
from contextlib import contextmanager


_DB_INITIALIZED = False
_DB_INIT_LOCK = Lock()

BASE_DIR = Path(__file__).resolve().parents[2]

MARKET_DB_PATH = BASE_DIR / "data" / "market_data.db"
LOG_DB_PATH = BASE_DIR / "data" / "logs.db"

DB_PATH = MARKET_DB_PATH  # backwards-compatible default

# -------------------------------------------------------------------
# Connection Factories
# -------------------------------------------------------------------
def get_connection(db_path=MARKET_DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        db_path,
        timeout=30,
    )

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")

    return conn



def get_log_connection():
    return get_connection(LOG_DB_PATH)



# -------------------------------------------------------------------
# Connection Context Managers
# -------------------------------------------------------------------
@contextmanager
def market_db_connection():
    conn = get_connection()

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


@contextmanager
def get_row_connection():
    with market_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        yield conn


@contextmanager
def log_db_connection():
    conn = get_log_connection()

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()



# -------------------------------------------------------------------
# Database Initialization
# -------------------------------------------------------------------
def ensure_db_initialized():
    global _DB_INITIALIZED

    if _DB_INITIALIZED:
        return

    with _DB_INIT_LOCK:
        if not _DB_INITIALIZED:
            init_db()
            _DB_INITIALIZED = True


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
            CREATE TABLE IF NOT EXISTS alert_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                metric TEXT NOT NULL,
                operator TEXT NOT NULL,
                threshold REAL NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                auto_disable_on_trigger INTEGER NOT NULL DEFAULT 1,
                trigger_count INTEGER NOT NULL DEFAULT 0,
                last_triggered_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN rule_type TEXT DEFAULT 'threshold'")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN direction TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN price_change_pct REAL")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN volume_change_pct REAL")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("""
                ALTER TABLE alert_rules
                ADD COLUMN require_volume_confirmation INTEGER DEFAULT 1
            """)
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN window_size INTEGER")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN auto_generated INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN source TEXT")
        except sqlite3.OperationalError:
            pass


        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN cooldown_seconds INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN last_triggered_price REAL")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE alert_rules ADD COLUMN last_triggered_quote_time TEXT")
        except sqlite3.OperationalError:
            pass

    init_streamer_control_table()
    init_log_db()


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



def init_log_db():
    LOG_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(LOG_DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")

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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                service TEXT,
                status TEXT,
                message TEXT,
                metadata_json TEXT
            )
        """)



# -------------------------------------------------------------------
# Quote Persistence
# -------------------------------------------------------------------
def save_quote_with_connection(conn, quote):
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
        quote.get("timestamp") or datetime.now(UTC).isoformat(),
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

    # commit handled by caller


def save_quote(quote):
    with market_db_connection() as conn:
        save_quote_with_connection(conn, quote)



# -------------------------------------------------------------------
# Alert Persistence and Queries
# -------------------------------------------------------------------
def clear_alerts():
    with market_db_connection() as conn:
        conn.execute("DELETE FROM alerts")



def clear_alert_rules():
    with market_db_connection() as conn:
        conn.execute("DELETE FROM alert_rules")



def save_alert(alert):
    with market_db_connection() as conn:
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
    with market_db_connection() as conn:
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



# -------------------------------------------------------------------
# Provider and System Event Logging
# -------------------------------------------------------------------
def save_provider_error(
    provider,
    symbol=None,
    operation=None,
    error_type=None,
    message=None,
    raw_response=None,
):
    try:
        if raw_response is not None and not isinstance(raw_response, str):
            raw_response = json.dumps(raw_response, default=str)

        with log_db_connection() as conn:
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

    except Exception as e:
        print(f"FAILED TO SAVE PROVIDER ERROR: {type(e).__name__}: {e}")


def save_system_event(
    event_type,
    service=None,
    status=None,
    message=None,
    metadata=None,
):
    try:
        metadata_json = None
        if metadata is not None:
            metadata_json = json.dumps(metadata, default=str)

        with log_db_connection() as conn:
            conn.execute("""
                INSERT INTO system_events (
                    timestamp,
                    event_type,
                    service,
                    status,
                    message,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(UTC).isoformat(),
                event_type,
                service,
                status,
                message,
                metadata_json,
            ))

    except Exception as e:
        print(f"FAILED TO SAVE SYSTEM EVENT: {type(e).__name__}: {e}")
