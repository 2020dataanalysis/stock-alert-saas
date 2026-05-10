from app.signals.whale_rule_engine import evaluate_whale_rule, price_windows, volume_windows


def clear_windows():
    price_windows.clear()
    volume_windows.clear()


def test_whale_spike_triggers_after_window_filled():
    clear_windows()

    rule = {
        "symbol": "AAPL",
        "rule_type": "whale_spike",
        "direction": "up",
        "price_change_pct": 1.0,
        "volume_change_pct": 10.0,
        "window_size": 3,
    }

    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 100, "volume": 1000}) is False
    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 100.5, "volume": 1050}) is False
    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 102, "volume": 1200}) is True


def test_whale_drop_triggers_after_window_filled():
    clear_windows()

    rule = {
        "symbol": "AAPL",
        "rule_type": "whale_drop",
        "direction": "down",
        "price_change_pct": 1.0,
        "volume_change_pct": 10.0,
        "window_size": 3,
    }

    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 100, "volume": 1000}) is False
    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 99.5, "volume": 1050}) is False
    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 98, "volume": 1200}) is True


def test_whale_rule_requires_volume_confirmation():
    clear_windows()

    rule = {
        "symbol": "AAPL",
        "rule_type": "whale_spike",
        "direction": "up",
        "price_change_pct": 1.0,
        "volume_change_pct": 50.0,
        "window_size": 3,
    }

    evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 100, "volume": 1000})
    evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 100.5, "volume": 1010})

    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 102, "volume": 1100}) is False


def test_whale_windows_are_symbol_specific():
    clear_windows()

    rule = {
        "symbol": "AAPL",
        "rule_type": "whale_spike",
        "direction": "up",
        "price_change_pct": 1.0,
        "volume_change_pct": 10.0,
        "window_size": 3,
    }

    evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 100, "volume": 1000})
    evaluate_whale_rule(rule, {"symbol": "MSFT", "last": 200, "volume": 1000})
    evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 100.5, "volume": 1050})

    assert evaluate_whale_rule(rule, {"symbol": "AAPL", "last": 102, "volume": 1200}) is True
