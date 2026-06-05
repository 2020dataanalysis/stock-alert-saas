from collections import defaultdict, deque


price_windows = defaultdict(lambda: deque(maxlen=100))
volume_windows = defaultdict(lambda: deque(maxlen=100))


def evaluate_whale_rule(rule, quote):
    symbol = quote["symbol"]

    price_windows[symbol].append(quote["last"])
    volume_windows[symbol].append(quote["volume"])

    window_size = rule["window_size"]

    if len(price_windows[symbol]) < window_size:
        return False

    start_price = list(price_windows[symbol])[-window_size]
    current_price = quote["last"]

    start_volume = list(volume_windows[symbol])[-window_size]
    current_volume = quote["volume"]

    if start_price == 0 or start_volume == 0:
        return False

    price_change_pct = (
        (current_price - start_price)
        / start_price
    ) * 100

    volume_change_pct = (
        (current_volume - start_volume)
        / start_volume
    ) * 100

    direction = rule["direction"]

    required_price_change = rule["price_change_pct"]
    required_volume_change = rule["volume_change_pct"]

    if rule["require_volume_confirmation"]:

        if volume_change_pct < required_volume_change:
            return False
    
    price_triggered = False

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
