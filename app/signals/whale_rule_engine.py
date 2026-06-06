from collections import defaultdict, deque


price_windows = defaultdict(lambda: deque(maxlen=100))
volume_windows = defaultdict(lambda: deque(maxlen=100))


def create_rule_windows():
    return {
        "price_windows": defaultdict(lambda: deque(maxlen=100)),
        "volume_windows": defaultdict(lambda: deque(maxlen=100)),
    }


def evaluate_whale_rule(rule, quote, windows=None):
    if windows is None:
        windows = {
            "price_windows": price_windows,
            "volume_windows": volume_windows,
        }

    local_price_windows = windows["price_windows"]
    local_volume_windows = windows["volume_windows"]

    symbol = quote["symbol"]

    local_price_windows[symbol].append(quote["last"])
    local_volume_windows[symbol].append(quote["volume"])

    window_size = rule["window_size"]

    if len(local_price_windows[symbol]) < window_size:
        return False

    start_price = list(local_price_windows[symbol])[-window_size]
    current_price = quote["last"]

    start_volume = list(local_volume_windows[symbol])[-window_size]
    current_volume = quote["volume"]

    if start_price == 0 or start_volume == 0:
        return False

    price_change_pct = ((current_price - start_price) / start_price) * 100
    volume_change_pct = ((current_volume - start_volume) / start_volume) * 100

    direction = rule["direction"]
    required_price_change = rule["price_change_pct"]
    required_volume_change = rule["volume_change_pct"]

    price_move_type = rule["price_move_type"] or "percent"
    required_price_move_cents = rule["price_move_cents"] or 0

    price_delta = current_price - start_price
    required_price_delta = required_price_move_cents / 100

    if rule["require_volume_confirmation"]:
        if volume_change_pct < required_volume_change:
            return False

    price_triggered = False

    if price_move_type == "cents":
        if direction == "up":
            price_triggered = price_delta >= required_price_delta
        elif direction == "down":
            price_triggered = price_delta <= -required_price_delta
    else:
        if direction == "up":
            price_triggered = price_change_pct >= required_price_change
        elif direction == "down":
            price_triggered = price_change_pct <= -required_price_change

    if not price_triggered:
        return False

    return {
        "price_change_pct": round(price_change_pct, 4),
        "volume_change_pct": round(volume_change_pct, 4),
        "oldest_price": start_price,
        "newest_price": current_price,
        "oldest_volume": start_volume,
        "newest_volume": current_volume,
    }
