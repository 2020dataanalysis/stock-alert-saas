def classify_market_state(features):

    shock_score = features["shock_score"]
    trend_score = features["trend_score"]
    noise_score = features["noise_score"]
    velocity_5s_pct = features["velocity_5s_pct"]
    velocity_10s_pct = features["velocity_10s_pct"]

    if shock_score >= 3:

        if velocity_5s_pct < 0:
            return {
                "state": "SELL_SHOCK",
                "trade_permission": "BLOCK",
                "confidence_score": shock_score,
                "message": "Fast downside move detected"
            }

        return {
            "state": "BUY_SHOCK",
            "trade_permission": "CAUTION",
            "confidence_score": shock_score,
            "message": "Fast upside move detected"
        }

    if noise_score >= 4 and trend_score < 2:
        return {
            "state": "CHOPPY",
            "trade_permission": "BLOCK",
            "confidence_score": noise_score,
            "message": "Noisy range movement detected"
        }

    if trend_score >= 2:

        if velocity_10s_pct > 0:
            return {
                "state": "UP_TREND",
                "trade_permission": "ALLOW",
                "confidence_score": trend_score,
                "message": "Short-term upside trend detected"
            }

        return {
            "state": "DOWN_TREND",
            "trade_permission": "CAUTION",
            "confidence_score": trend_score,
            "message": "Short-term downside trend detected"
        }

    return {
        "state": "NORMAL",
        "trade_permission": "WAIT",
        "confidence_score": 0,
        "message": "No strong market condition detected"
    }
