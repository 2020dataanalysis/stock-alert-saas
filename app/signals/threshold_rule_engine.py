def evaluate_threshold_rule(rule, quote):
    metric = rule["metric"]

    if metric not in quote:
        return False

    value = quote[metric]
    threshold = rule["threshold"]
    operator = rule["operator"]

    if operator == ">":
        return value > threshold

    if operator == "<":
        return value < threshold

    if operator == ">=":
        return value >= threshold

    if operator == "<=":
        return value <= threshold

    return False
