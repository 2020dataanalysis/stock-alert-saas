import sqlite3
from datetime import datetime, UTC
from pathlib import Path

DB_PATH = Path("data/market_data.db")


def get_alert_rules():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT
                id,
                symbol,
                metric,
                operator,
                threshold,
                is_active,
                auto_disable_on_trigger,
                trigger_count,
                last_triggered_at,
                created_at,
                updated_at
            FROM alert_rules
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def create_alert_rule(
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
                metric,
                operator,
                threshold,
                is_active,
                auto_disable_on_trigger,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
