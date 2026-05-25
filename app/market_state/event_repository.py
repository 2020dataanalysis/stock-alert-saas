from app.market_state.db import get_connection


def save_event(
    timestamp,
    symbol,
    event_type,
    price,
    velocity_pct,
    confidence_score,
    message
):

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO market_state_events (
                timestamp,
                symbol,
                event_type,
                price,
                velocity_pct,
                confidence_score,
                message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                symbol,
                event_type,
                price,
                velocity_pct,
                confidence_score,
                message
            )
        )

        conn.commit()
