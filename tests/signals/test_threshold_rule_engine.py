from app.signals.threshold_rule_engine import evaluate_threshold_rule


def test_threshold_greater_than_triggers():
    rule = {"metric": "last", "operator": ">", "threshold": 100}
    quote = {"last": 101}

    assert evaluate_threshold_rule(rule, quote) is True


def test_threshold_greater_than_does_not_trigger():
    rule = {"metric": "last", "operator": ">", "threshold": 100}
    quote = {"last": 99}

    assert evaluate_threshold_rule(rule, quote) is False


def test_threshold_less_than_triggers():
    rule = {"metric": "last", "operator": "<", "threshold": 100}
    quote = {"last": 99}

    assert evaluate_threshold_rule(rule, quote) is True


def test_threshold_missing_metric_does_not_trigger():
    rule = {"metric": "last", "operator": ">", "threshold": 100}
    quote = {"bid": 101}

    assert evaluate_threshold_rule(rule, quote) is False


def test_threshold_unknown_operator_does_not_trigger():
    rule = {"metric": "last", "operator": "==", "threshold": 100}
    quote = {"last": 100}

    assert evaluate_threshold_rule(rule, quote) is False
