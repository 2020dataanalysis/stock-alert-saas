from collections import deque
from datetime import datetime


class FeatureEngine:

    def __init__(self):

        self.events = deque()

    def parse_timestamp(self, timestamp):

        return datetime.fromisoformat(timestamp)

    def prune_old_events(self, current_time, max_seconds=30):

        while self.events:

            oldest_time = self.events[0]["time"]
            age_seconds = (
                current_time - oldest_time
            ).total_seconds()

            if age_seconds <= max_seconds:
                break

            self.events.popleft()

    def get_window_prices(self, current_time, seconds):

        prices = []

        for event in self.events:

            age_seconds = (
                current_time - event["time"]
            ).total_seconds()

            if age_seconds <= seconds:
                prices.append(event["price"])

        return prices

    def calculate_velocity(self, prices):

        if len(prices) < 2:
            return 0

        first_price = prices[0]
        last_price = prices[-1]

        if first_price == 0:
            return 0

        return (
            (last_price - first_price)
            / first_price
        ) * 100

    def calculate_range(self, prices):

        if len(prices) < 2:
            return 0

        low_price = min(prices)
        high_price = max(prices)

        if low_price == 0:
            return 0

        return (
            (high_price - low_price)
            / low_price
        ) * 100

    def update(self, timestamp, price):

        current_time = self.parse_timestamp(timestamp)

        self.events.append({
            "time": current_time,
            "price": price,
        })

        self.prune_old_events(
            current_time=current_time,
            max_seconds=30
        )

        prices_5s = self.get_window_prices(
            current_time=current_time,
            seconds=5
        )

        prices_10s = self.get_window_prices(
            current_time=current_time,
            seconds=10
        )

        prices_30s = self.get_window_prices(
            current_time=current_time,
            seconds=30
        )

        velocity_5s_pct = self.calculate_velocity(prices_5s)
        velocity_10s_pct = self.calculate_velocity(prices_10s)
        range_30s_pct = self.calculate_range(prices_30s)

        shock_score = min(
            abs(velocity_5s_pct) * 40,
            100
        )

        trend_score = min(
            abs(velocity_10s_pct) * 25,
            100
        )

        noise_score = min(
            range_30s_pct * 20,
            100
        )

        return {
            "velocity_5s_pct": velocity_5s_pct,
            "velocity_10s_pct": velocity_10s_pct,
            "range_30s_pct": range_30s_pct,
            "shock_score": shock_score,
            "trend_score": trend_score,
            "noise_score": noise_score,
        }
