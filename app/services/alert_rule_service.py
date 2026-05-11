import sqlite3
from datetime import datetime, UTC
from pathlib import Path
from datetime import timedelta

DB_PATH = Path("data/market_data.db")

def get_active_alert_rules():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT *
            FROM alert_rules
            WHERE is_active = 1
            ORDER BY id DESC
        """)

        return cursor.fetchall()

def get_alert_rules():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT
                id,
                symbol,
                rule_type,
                direction,
                metric,
                operator,
                threshold,
                price_change_pct,
                volume_change_pct,
                window_size,
                is_active,
                auto_disable_on_trigger,
                auto_generated,
                source,
                trigger_count,
                last_triggered_at,
                created_at,
                updated_at
            FROM alert_rules
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def create_threshold_rule(
    symbol,
    metric,
    operator,
    threshold,
    is_active=True,
    auto_disable_on_trigger=True,
):
    now = datetime.now(UTC).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO alert_rules (
                symbol,
                rule_type,
                metric,
                operator,
                threshold,
                is_active,
                auto_disable_on_trigger,
                auto_generated,
                source,
                created_at,
                updated_at
            )
            VALUES (?, 'threshold', ?, ?, ?, ?, ?, 0, NULL, ?, ?)
        """, (
            symbol.upper(),
            metric,
            operator,
            float(threshold),
            int(is_active),
            int(auto_disable_on_trigger),
            now,
            now,
        ))


def create_whale_rule(
    symbol,
    direction,
    price_change_pct,
    volume_change_pct,
    window_size,
    is_active=True,
    auto_disable_on_trigger=True,
    auto_generated=False,
    source=None,
):
    now = datetime.now(UTC).isoformat()

    rule_type = "whale_spike" if direction == "up" else "whale_drop"

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO alert_rules (
                symbol,
                rule_type,
                direction,
                metric,
                operator,
                threshold,
                price_change_pct,
                volume_change_pct,
                window_size,
                is_active,
                auto_disable_on_trigger,
                auto_generated,
                source,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, 'price_change_pct', '>=', 0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol.upper(),
            rule_type,
            direction,
            float(price_change_pct),
            float(volume_change_pct),
            int(window_size),
            int(is_active),
            int(auto_disable_on_trigger),
            int(auto_generated),
            source,
            now,
            now,
        ))


# Backward-compatible name used by existing dashboard route.
def create_alert_rule(
    symbol,
    metric,
    operator,
    threshold,
    is_active=True,
    auto_disable_on_trigger=True,
):
    create_threshold_rule(
        symbol=symbol,
        metric=metric,
        operator=operator,
        threshold=threshold,
        is_active=is_active,
        auto_disable_on_trigger=auto_disable_on_trigger,
    )


def get_active_alert_rules():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT *
            FROM alert_rules
            WHERE is_active = 1
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def set_alert_rule_active(rule_id, is_active):
    now = datetime.now(UTC).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE alert_rules
            SET is_active = ?, updated_at = ?
            WHERE id = ?
        """, (
            int(is_active),
            now,
            rule_id,
        ))


def delete_alert_rule(rule_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            DELETE FROM alert_rules
            WHERE id = ?
        """, (rule_id,))


def mark_rule_triggered(rule_id, quote):
    now = datetime.now(UTC).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE alert_rules
            SET
                trigger_count = trigger_count + 1,
                last_triggered_at = ?,
                last_triggered_price = ?,
                last_triggered_quote_time = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            now,
            quote.get("last"),
            quote.get("timestamp"),
            now,
            rule_id,
        ))


def disable_rule(rule_id):
    now = datetime.now(UTC).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE alert_rules
            SET
                is_active = 0,
                updated_at = ?
            WHERE id = ?
        """, (
            now,
            rule_id,
        ))


def is_rule_in_cooldown(rule):
    if not rule["last_triggered_at"]:
        return False

    cooldown_seconds = rule["cooldown_seconds"] or 0

    if cooldown_seconds <= 0:
        return False

    last_trigger = datetime.fromisoformat(rule["last_triggered_at"])

    return (
        datetime.now(UTC) - last_trigger
    ) < timedelta(seconds=cooldown_seconds)


def mover_rule_exists(symbol, direction):
    rule_type = "whale_spike" if direction == "up" else "whale_drop"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT 1
            FROM alert_rules
            WHERE
                symbol = ?
                AND rule_type = ?
                AND auto_generated = 1
            LIMIT 1
        """, (
            symbol.upper(),
            rule_type,
        ))

        return cursor.fetchone() is not None


def generate_mover_rules(
    movers,
    price_change_pct=1.5,
    volume_change_pct=20,
    window_size=5,
):
    created = 0

    for symbol in movers:

        if not mover_rule_exists(symbol, "up"):
            create_whale_rule(
                symbol=symbol,
                direction="up",
                price_change_pct=price_change_pct,
                volume_change_pct=volume_change_pct,
                window_size=window_size,
                auto_generated=True,
                source="movers",
            )
            created += 1

        if not mover_rule_exists(symbol, "down"):
            create_whale_rule(
                symbol=symbol,
                direction="down",
                price_change_pct=price_change_pct,
                volume_change_pct=volume_change_pct,
                window_size=window_size,
                auto_generated=True,
                source="movers",
            )
            created += 1

    return created