from pathlib import Path
import sqlite3
from contextlib import closing

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


        conn.execute("""
            CREATE TABLE IF NOT EXISTS historical_bars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp, timeframe)
            )
        """)

        conn.commit()


def create_opening_scenario(
    symbol,
    trade_date,
    gap_pct,
    open_price,
    previous_close,
):
    with get_historical_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO opening_scenarios (
                symbol,
                trade_date,
                gap_pct,
                open_price,
                previous_close
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            symbol,
            trade_date,
            gap_pct,
            open_price,
            previous_close,
        ))

        conn.commit()

        return cursor.lastrowid


def get_minute_outcomes(
    scenario_id,
):
    with get_historical_connection() as conn:

        rows = conn.execute("""
            SELECT
                id,
                minute_number,
                price,
                distance_from_open_pct,
                broke_below_open,
                broke_above_open,
                created_at
            FROM minute_outcomes
            WHERE scenario_id = ?
            ORDER BY minute_number
        """, (
            scenario_id,
        )).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def add_minute_outcome(
    scenario_id,
    minute_number,
    price,
    open_price,
):
    distance_from_open_pct = (
        ((price - open_price) / open_price) * 100
    )

    broke_below_open = int(
        price < open_price
    )

    broke_above_open = int(
        price > open_price
    )

    with get_historical_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO minute_outcomes (
                scenario_id,
                minute_number,
                price,
                distance_from_open_pct,
                broke_below_open,
                broke_above_open
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            scenario_id,
            minute_number,
            price,
            distance_from_open_pct,
            broke_below_open,
            broke_above_open,
        ))

        conn.commit()

        return cursor.lastrowid


def get_recent_opening_scenarios(limit=20):
    with get_historical_connection() as conn:
        rows = conn.execute("""
            SELECT
                id,
                symbol,
                trade_date,
                gap_pct,
                open_price,
                previous_close,
                created_at
            FROM opening_scenarios
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def upsert_historical_bar(
    symbol,
    timestamp,
    timeframe,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
):
    with get_historical_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO historical_bars (
                symbol,
                timestamp,
                timeframe,
                open,
                high,
                low,
                close,
                volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, timestamp, timeframe)
            DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume
        """, (
            symbol,
            timestamp,
            timeframe,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
        ))

        conn.commit()

        return cursor.lastrowid


def get_historical_bars(
    symbol,
    timeframe,
    start_timestamp=None,
    end_timestamp=None,
    limit=500,
):
    query = """
        SELECT
            id,
            symbol,
            timestamp,
            timeframe,
            open,
            high,
            low,
            close,
            volume
        FROM historical_bars
        WHERE symbol = ?
          AND timeframe = ?
    """

    params = [
        symbol,
        timeframe,
    ]

    if start_timestamp is not None:
        query += " AND timestamp >= ?"
        params.append(start_timestamp)

    if end_timestamp is not None:
        query += " AND timestamp <= ?"
        params.append(end_timestamp)

    query += """
        ORDER BY timestamp DESC
        LIMIT ?
    """

    params.append(limit)

    with get_historical_connection() as conn:
        rows = conn.execute(
            query,
            params,
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def upsert_historical_bars(
    bars,
):
    with closing(get_historical_connection()) as conn:
        conn.executemany("""
            INSERT INTO historical_bars (
                symbol,
                timestamp,
                timeframe,
                open,
                high,
                low,
                close,
                volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, timestamp, timeframe)
            DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume
        """, bars)

        conn.commit()

    return len(bars)