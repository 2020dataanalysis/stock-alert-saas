from app.market_state.storage.db import get_connection


def save_snapshot(
    timestamp,
    symbol,
    price,
    shock_score,
    trend_score,
    noise_score,
    state,
    trade_permission
):

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO market_state_snapshots (
                timestamp,
                symbol,
                price,
                shock_score,
                trend_score,
                noise_score,
                state,
                trade_permission
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                symbol,
                price,
                shock_score,
                trend_score,
                noise_score,
                state,
                trade_permission
            )
        )

        conn.commit()
