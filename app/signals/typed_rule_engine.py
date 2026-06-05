from app.services.alert_rule_service import (
    get_active_alert_rules,
    mark_rule_triggered,
    disable_rule,
    is_rule_in_cooldown,
)
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

        if is_rule_in_cooldown(rule):
            continue

        triggered = False
        trigger_details = {}

        if rule["rule_type"] == "threshold":
            triggered = evaluate_threshold_rule(rule, quote)

        elif rule["rule_type"] in {"whale_spike", "whale_drop"}:
            trigger_details = evaluate_whale_rule(rule, quote)
            triggered = bool(trigger_details)

        if triggered:

            mark_rule_triggered(rule["id"], quote)

            if rule["auto_disable_on_trigger"]:
                disable_rule(rule["id"])

            alert = {
                "symbol": quote["symbol"],
                "type": rule["rule_type"],
                "rule_id": rule["id"],
                "message": f'{quote["symbol"]} triggered {rule["rule_type"]}',
            }

            alert.update(trigger_details)

            triggered_alerts.append(alert)

    return triggered_alerts