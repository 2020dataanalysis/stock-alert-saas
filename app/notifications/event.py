from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class AlertEvent:
    alert_type: str
    symbol: str
    title: str
    message: str
    occurred_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    details: dict[str, Any] = field(default_factory=dict)

    def as_payload(self) -> dict[str, Any]:
        return {
            "type": self.alert_type,
            "symbol": self.symbol.upper(),
            "title": self.title,
            "message": self.message,
            "occurred_at": self.occurred_at,
            **self.details,
        }
