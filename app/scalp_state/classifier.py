def classify_scalp_state(symbol, recent_quotes):
    if not recent_quotes:
        return {
            "symbol": symbol,
            "state": "NO_DATA",
            "score": 0,
            "action": "WAIT",
            "reason": "No recent quote data available.",
        }

    prices = [
        quote["last"]
        for quote in recent_quotes
        if quote.get("last") is not None
    ]

    if len(prices) < 3:
        return {
            "symbol": symbol,
            "state": "NO_DATA",
            "score": 0,
            "action": "WAIT",
            "reason": "Not enough recent quotes to classify.",
        }

    high = max(prices)
    low = min(prices)
    latest = prices[-1]

    range_pct = ((high - low) / latest) * 100

    if range_pct < 0.15:
        state = "AVOID_CHOP"
        score = 20
        action = "DO_NOT_TRADE"
        reason = "Range is too tight; tight stops likely get chopped."
    elif range_pct < 0.35:
        state = "BUILDING_COMPRESSION"
        score = 60
        action = "WAIT"
        reason = "Compression is forming; wait for expansion."
    else:
        state = "ACTIVE_EXPANSION"
        score = 85
        action = "WATCH_FOR_SCALP"
        reason = "Range has expanded enough for scalp conditions."

    return {
        "symbol": symbol,
        "state": state,
        "score": score,
        "action": action,
        "reason": reason,
        "range_pct": round(range_pct, 3),
        "latest": latest,
        "volume_samples": len(prices),
    }
