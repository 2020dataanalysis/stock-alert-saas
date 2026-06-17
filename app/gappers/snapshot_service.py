from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from app.gappers.db_init import get_gap_connection


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _payload_to_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _payload_hash(payload_json: str) -> str:
    return hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()


def initialize_gap_snapshot_table() -> None:
    with get_gap_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS gap_dashboard_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                captured_at TEXT NOT NULL,
                page TEXT NOT NULL,
                source_url TEXT NOT NULL,
                snapshot_key TEXT NOT NULL DEFAULT 'gappers',
                payload_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(gap_dashboard_snapshots)"
            ).fetchall()
        }

        if "snapshot_key" not in columns:
            conn.execute(
                """
                ALTER TABLE gap_dashboard_snapshots
                ADD COLUMN snapshot_key TEXT NOT NULL DEFAULT 'gappers'
                """
            )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_gap_dashboard_snapshots_page_key_time
            ON gap_dashboard_snapshots(page, snapshot_key, captured_at)
            """
        )


def save_gap_dashboard_snapshot_if_changed(
    *,
    page: str,
    source_url: str,
    snapshot_key: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    initialize_gap_snapshot_table()

    payload_json = _payload_to_json(payload)
    current_hash = _payload_hash(payload_json)
    now = _utc_now_iso()

    with get_gap_connection() as conn:
        previous = conn.execute(
            """
            SELECT id, payload_hash
            FROM gap_dashboard_snapshots
            WHERE page = ?
              AND snapshot_key = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (page, snapshot_key),
        ).fetchone()

        if previous and previous["payload_hash"] == current_hash:
            return {
                "saved": False,
                "reason": "unchanged",
                "previous_snapshot_id": previous["id"],
                "payload_hash": current_hash,
            }

        cursor = conn.execute(
            """
            INSERT INTO gap_dashboard_snapshots (
                captured_at,
                page,
                source_url,
                snapshot_key,
                payload_hash,
                payload_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now,
                page,
                source_url,
                snapshot_key,
                current_hash,
                payload_json,
                now,
            ),
        )

        return {
            "saved": True,
            "snapshot_id": cursor.lastrowid,
            "payload_hash": current_hash,
            "captured_at": now,
        }
