from app.signals.typed_rule_engine import evaluate_typed_rules


def test_threshold_rule_triggers():

    rule = {
        "id": 1,
        "symbol": "AAPL",
        "rule_type": "threshold",
        "metric": "last",
        "operator": ">",
        "threshold": 200,
        "is_active": 1,
        "auto_disable_on_trigger": 0,
        "last_triggered_at": None,
        "cooldown_seconds": 0,
    }

    quote = {
        "symbol": "AAPL",
        "last": 250,
        "timestamp": "2026-05-10T12:00:00+00:00",
    }

    alerts = []

    from app.signals.threshold_rule_engine import evaluate_threshold_rule

    triggered = evaluate_threshold_rule(rule, quote)

    if triggered:
        alerts.append({
            "symbol": quote["symbol"],
            "type": rule["rule_type"],
        })

    assert len(alerts) == 1
    assert alerts[0]["symbol"] == "AAPL"