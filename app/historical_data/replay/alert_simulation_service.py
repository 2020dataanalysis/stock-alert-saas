from app.services.alert_rule_service import get_active_alert_rules
from app.signals.whale_rule_engine import (
    create_rule_windows,
    evaluate_whale_rule,
)


def simulate_replay_alerts(quotes):
    rules = get_active_alert_rules()
    windows = create_rule_windows()
    simulated_alerts = []

    sorted_quotes = sorted(
        quotes,
        key=lambda quote: quote.get("timestamp") or "",
    )

    for quote in sorted_quotes:
        quote_symbol = quote.get("symbol")

        for rule in rules:
            if rule["symbol"] != quote_symbol:
                continue

            if rule["rule_type"] not in ("whale_spike", "whale_drop"):
                continue

            result = evaluate_whale_rule(
                rule=rule,
                quote=quote,
                windows=windows,
            )

            if not result:
                continue

            simulated_alerts.append({
                "mode": "replay",
                "symbol": quote_symbol,
                "timestamp": quote.get("timestamp"),
                "rule_id": rule["id"],
                "rule_type": rule["rule_type"],
                "direction": rule["direction"],
                "last": quote.get("last"),
                "volume": quote.get("volume"),
                "details": result,
            })

    return simulated_alerts
