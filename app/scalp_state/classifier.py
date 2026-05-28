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
    compression_maturity_score=None,
    compression_label=None,
    expansion_exhaustion_score=None,
    expansion_exhaustion_label=None,
    volume_samples=0,
    volume_delta=None,
    volume_delta_per_sample=None,
    volume_efficiency=None,
    relative_volume_ratio=None,
    relative_volume_label=None,
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
        "compression_maturity_score": compression_maturity_score,
        "compression_label": compression_label,
        "expansion_exhaustion_score": expansion_exhaustion_score,
        "expansion_exhaustion_label": expansion_exhaustion_label,
        "volume_samples": volume_samples,
        "volume_delta": volume_delta,
        "volume_delta_per_sample": volume_delta_per_sample,
        "volume_efficiency": volume_efficiency,
        "relative_volume_ratio": relative_volume_ratio,
        "relative_volume_label": relative_volume_label,
    }

def extract_prices(recent_quotes):
    return [
        quote["last"]
        for quote in recent_quotes
        if quote.get("last") is not None
    ]

def extract_volumes(recent_quotes):
    return [
        quote["volume"]
        for quote in recent_quotes
        if quote.get("volume") is not None
    ]


# def calculate_volume_features(volumes):
#     if len(volumes) < 2:
#         return {
#             "volume_delta": 0,
#             "volume_samples": len(volumes),
#         }

#     volume_delta = (
#         volumes[-1] - volumes[0]
#     )

#     return {
#         "volume_delta": volume_delta,
#         "volume_samples": len(volumes),
#     }


def calculate_volume_features(prices, volumes):
    if len(volumes) < 2 or len(prices) < 2:
        return {
            "volume_delta": 0,
            "volume_delta_per_sample": 0,
            "volume_efficiency": 0,
            "volume_samples": len(volumes),
        }

    volume_delta = (
        volumes[-1] - volumes[0]
    )

    volume_delta_per_sample = (
        volume_delta /
        max(len(volumes) - 1, 1)
    )

    price_move_pct = abs(
        ((prices[-1] - prices[0]) / prices[0]) * 100
    )

    if volume_delta <= 0:
        volume_efficiency = 0
    else:
        volume_efficiency = (
            price_move_pct /
            (volume_delta / 1000)
        )

    return {
        "volume_delta": volume_delta,
        "volume_delta_per_sample": round(
            volume_delta_per_sample,
            2
        ),
        "volume_efficiency": round(
            volume_efficiency,
            6
        ),
        "volume_samples": len(volumes),
    }


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


def calculate_compression_maturity(features):
    range_pct = features["range_pct"]
    range_velocity = features["range_velocity"]
    directional_efficiency = features["directional_efficiency"]

    score = 0

    if range_pct < 0.35:
        score += 40

    if range_velocity < 1.2:
        score += 30

    if directional_efficiency < 0.3:
        score += 30

    if score >= 80:
        label = "READY_FOR_EXPANSION"
    elif score >= 50:
        label = "MATURING_COMPRESSION"
    elif score > 0:
        label = "EARLY_COMPRESSION"
    else:
        label = "NOT_COMPRESSING"

    return {
        "compression_maturity_score": score,
        "compression_label": label,
    }

def calculate_expansion_exhaustion(features):
    range_pct = features["range_pct"]
    range_velocity = features["range_velocity"]
    directional_efficiency = features["directional_efficiency"]

    score = 0

    if range_pct > 0.35:
        score += 30

    if range_velocity > 2.0:
        score += 30

    if directional_efficiency < 0.25:
        score += 40

    if score >= 80:
        label = "POSSIBLE_EXHAUSTION"
    elif score >= 50:
        label = "EXTENDED_EXPANSION"
    elif score > 0:
        label = "EARLY_EXPANSION"
    else:
        label = "NOT_EXPANDING"

    return {
        "expansion_exhaustion_score": score,
        "expansion_exhaustion_label": label,
    }

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

    features = {
        "latest": latest,
        "range_pct": recent_range_pct,
        "older_range_pct": older_range_pct,
        "recent_range_pct": recent_range_pct,
        "range_velocity": range_velocity,
        "directional_efficiency":
            directional_efficiency,
    }

    features.update(
        calculate_compression_maturity(
            features
        )
    )

    features.update(
        calculate_expansion_exhaustion(
            features
        )
    )


    return features


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
        and directional_efficiency < 0.25
    ):
        return {
            "state": "NOISY_EXPANSION",
            "score": 45,
            "action": "WAIT",
            "reason": "Expansion is noisy; directional efficiency is weak.",
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

    volumes = extract_volumes(
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

    features.update(
        calculate_volume_features(
            prices,
            volumes,
        )
    )

    features.update(
        calculate_local_relative_volume(
            volumes
        )
    )


    decision = decide_scalp_state(
        features
    )

    return build_result(
        symbol=symbol,
        volume_samples=features["volume_samples"],
        volume_delta=features["volume_delta"],
        volume_delta_per_sample=features["volume_delta_per_sample"],
        volume_efficiency=features["volume_efficiency"],
        relative_volume_ratio=features["relative_volume_ratio"],
        relative_volume_label=features["relative_volume_label"],
        latest=features["latest"],
        range_pct=features["range_pct"],
        range_velocity=features["range_velocity"],
        older_range_pct=features["older_range_pct"],
        recent_range_pct=features["recent_range_pct"],
        directional_efficiency=features["directional_efficiency"],
        compression_maturity_score=features["compression_maturity_score"],
        compression_label=features["compression_label"],
        expansion_exhaustion_score=features["expansion_exhaustion_score"],
        expansion_exhaustion_label=features["expansion_exhaustion_label"],
        **decision,
    )


def calculate_local_relative_volume(volumes):
    if len(volumes) < 4:
        return {
            "relative_volume_ratio": 0,
            "relative_volume_label": "NO_DATA",
        }

    midpoint = len(volumes) // 2

    older_volumes = volumes[:midpoint]
    recent_volumes = volumes[midpoint:]

    older_delta = (
        older_volumes[-1] - older_volumes[0]
    )

    recent_delta = (
        recent_volumes[-1] - recent_volumes[0]
    )

    if older_delta <= 0:
        relative_volume_ratio = 0
    else:
        relative_volume_ratio = (
            recent_delta /
            older_delta
        )

    if relative_volume_ratio >= 3:
        label = "EXTREME_RVOL"
    elif relative_volume_ratio >= 2:
        label = "HIGH_RVOL"
    elif relative_volume_ratio >= 1.2:
        label = "ELEVATED_RVOL"
    elif relative_volume_ratio > 0:
        label = "NORMAL_RVOL"
    else:
        label = "NO_RVOL"

    return {
        "relative_volume_ratio": round(
            relative_volume_ratio,
            2
        ),
        "relative_volume_label": label,
    }