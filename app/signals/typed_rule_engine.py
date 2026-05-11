from app.services.alert_rule_service import get_active_alert_rules
from app.signals.threshold_rule_engine import evaluate_threshold_rule
from app.signals.whale_rule_engine import evaluate_whale_rule


def get_active_alert_rules_for_symbol(symbol):
    return [
        rule for rule in get_active_alert_rules()
        if rule["symbol"] == symbol
    ]


def evaluate_typed_rules(quote):
    triggered_alerts = []

    rules = get_active_alert_rules_for_symbol(quote["symbol"])

    for rule in rules:
        triggered = False

        if rule["rule_type"] == "threshold":
            triggered = evaluate_threshold_rule(rule, quote)

        elif rule["rule_type"] in {"whale_spike", "whale_drop"}:
            triggered = evaluate_whale_rule(rule, quote)

        if triggered:
            triggered_alerts.append({
                "symbol": quote["symbol"],
                "type": rule["rule_type"],
                "rule_id": rule["id"],
                "message": f'{quote["symbol"]} triggered {rule["rule_type"]}',
            })

    return triggered_alerts
