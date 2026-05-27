from app.scalp_state.classifier import classify_scalp_state
from app.storage.sqlite_store import market_db_connection
import sqlite3

DEFAULT_SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "TSLA",
    "WMT",
]


def get_recent_quotes_for_symbol(symbol, limit=50):

    with market_db_connection() as conn:

        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT
                symbol,
                last,
                volume,
                timestamp
            FROM quotes
            WHERE symbol = ?
            ORDER BY id DESC
            LIMIT ?
        """, (symbol, limit)).fetchall()

    quotes = [
        dict(row)
        for row in reversed(rows)
    ]

    return quotes



def get_scalp_state_rows(symbols=None):

    if symbols is None:
        symbols = DEFAULT_SYMBOLS

    rows = []

    for symbol in symbols:

        recent_quotes = get_recent_quotes_for_symbol(
            symbol=symbol,
            limit=50
        )

        rows.append(
            classify_scalp_state(
                symbol=symbol,
                recent_quotes=recent_quotes
            )
        )

    return rows
