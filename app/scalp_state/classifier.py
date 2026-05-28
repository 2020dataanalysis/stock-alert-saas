# app/scalp_state/classifier.py


NO_DATA_RESULT = {
    "state": "NO_DATA",
    "score": 0,
    "action": "WAIT",
}


def build_result(
    symbol,
    state,
    score,
    action,
    reason,
    latest=None,
    range_pct=None,
    range_velocity=None,
    older_range_pct=None,
    recent_range_pct=None,
    directional_efficiency=None,
    volume_samples=0,
):
    return {
        "symbol": symbol,
        "state": state,
        "score": score,
        "action": action,
        "reason": reason,
        "latest": latest,
        "range_pct": (
            round(range_pct, 3)
            if range_pct is not None
            else None
        ),
        "range_velocity": (
            round(range_velocity, 2)
            if range_velocity is not None
            else None
        ),
        "older_range_pct": (
            round(older_range_pct, 3)
            if older_range_pct is not None
            else None
        ),
        "recent_range_pct": (
            round(recent_range_pct, 3)
            if recent_range_pct is not None
            else None
        ),
        "directional_efficiency": (
            round(directional_efficiency, 2)
            if directional_efficiency is not None
            else None
        ),
        "volume_samples": volume_samples,
    }


def extract_prices(recent_quotes):
    return [
        quote["last"]
        for quote in recent_quotes
        if quote.get("last") is not None
    ]


def calculate_range_pct(prices, latest):
    high = max(prices)
    low = min(prices)

    return ((high - low) / latest) * 100


def calculate_directional_efficiency(prices):
    if len(prices) < 2:
        return 0.0

    net_move = abs(
        prices[-1] - prices[0]
    )

    total_move = 0.0

    for i in range(1, len(prices)):
        total_move += abs(
            prices[i] - prices[i - 1]
        )

    if total_move <= 0:
        return 0.0

    return net_move / total_move


def calculate_range_features(prices):
    midpoint = len(prices) // 2

    older_prices = prices[:midpoint]
    recent_prices = prices[midpoint:]

    latest = prices[-1]

    older_range_pct = calculate_range_pct(
        older_prices,
        latest,
    )

    recent_range_pct = calculate_range_pct(
        recent_prices,
        latest,
    )

    if older_range_pct <= 0:
        range_velocity = 1.0
    else:
        range_velocity = (
            recent_range_pct /
            older_range_pct
        )

    directional_efficiency = (
        calculate_directional_efficiency(
            prices
        )
    )

    return {
        "latest": latest,
        "range_pct": recent_range_pct,
        "older_range_pct": older_range_pct,
        "recent_range_pct": recent_range_pct,
        "range_velocity": range_velocity,
        "directional_efficiency": directional_efficiency,
    }


def decide_scalp_state(features):
    range_pct = features["range_pct"]
    range_velocity = features["range_velocity"]
    directional_efficiency = features["directional_efficiency"]

    if range_pct < 0.15:
        return {
            "state": "AVOID_CHOP",
            "score": 20,
            "action": "DO_NOT_TRADE",
            "reason": "Range too tight; likely chop.",
        }

    if (
        range_velocity > 1.8
        and directional_efficiency > 0.6
    ):
        return {
            "state": "HIGH_EFFICIENCY_EXPANSION",
            "score": 95,
            "action": "WATCH_FOR_SCALP",
            "reason": "Strong directional expansion detected.",
        }

    if range_velocity > 1.8:
        return {
            "state": "ACTIVE_EXPANSION",
            "score": 90,
            "action": "WATCH_FOR_SCALP",
            "reason": "Expansion velocity increasing rapidly.",
        }

    if range_pct < 0.35:
        return {
            "state": "BUILDING_COMPRESSION",
            "score": 60,
            "action": "WAIT",
            "reason": "Compression forming; waiting for expansion.",
        }

    return {
        "state": "ACTIVE_EXPANSION",
        "score": 80,
        "action": "WATCH_FOR_SCALP",
        "reason": "Range expansion active.",
    }


def classify_scalp_state(symbol, recent_quotes):
    if not recent_quotes:
        return build_result(
            symbol=symbol,
            reason="No recent quote data available.",
            volume_samples=0,
            **NO_DATA_RESULT,
        )

    prices = extract_prices(
        recent_quotes
    )

    if len(prices) < 3:
        return build_result(
            symbol=symbol,
            reason="Not enough recent quotes to classify.",
            volume_samples=len(prices),
            **NO_DATA_RESULT,
        )

    features = calculate_range_features(
        prices
    )

    decision = decide_scalp_state(
        features
    )

    return build_result(
        symbol=symbol,
        volume_samples=len(prices),
        latest=features["latest"],
        range_pct=features["range_pct"],
        range_velocity=features["range_velocity"],
        older_range_pct=features["older_range_pct"],
        recent_range_pct=features["recent_range_pct"],
        directional_efficiency=features["directional_efficiency"],
        **decision,
    )