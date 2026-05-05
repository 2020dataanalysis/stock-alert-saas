# app/signals/spike_detector.py

from collections import deque


class SpikeDetector:
    def __init__(
        self,
        price_spike_pct=0.5,
        volume_spike_pct=5,
        window_size=5,
    ):
        self.price_history = {}
        self.volume_history = {}

        self.price_spike_pct = price_spike_pct
        self.volume_spike_pct = volume_spike_pct
        self.window_size = window_size

    def process_quote(self, quote):
        symbol = quote["symbol"]
        price = quote["last"]
        volume = quote["volume"]

        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.window_size)
            self.volume_history[symbol] = deque(maxlen=self.window_size)

        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)

        # Wait until we have enough history
        if len(self.price_history[symbol]) < self.window_size:
            return []

        oldest_price = self.price_history[symbol][0]
        newest_price = self.price_history[symbol][-1]

        oldest_volume = self.volume_history[symbol][0]
        newest_volume = self.volume_history[symbol][-1]

        price_change_pct = ((newest_price - oldest_price) / oldest_price) * 100
        volume_change_pct = ((newest_volume - oldest_volume) / oldest_volume) * 100

        alerts = []

        # Price-only alert
        if abs(price_change_pct) >= self.price_spike_pct:
            alerts.append({
                "type": "PRICE_SPIKE",
                "symbol": symbol,
                "price_change_pct": round(price_change_pct, 2),
                "oldest_price": oldest_price,
                "newest_price": newest_price,
            })

        # Volume-only alert
        if volume_change_pct >= self.volume_spike_pct:
            alerts.append({
                "type": "VOLUME_SPIKE",
                "symbol": symbol,
                "volume_change_pct": round(volume_change_pct, 2),
                "oldest_volume": oldest_volume,
                "newest_volume": newest_volume,
            })

        # Stronger combined alert
        if (
            abs(price_change_pct) >= self.price_spike_pct
            and volume_change_pct >= self.volume_spike_pct
        ):
            alerts.append({
                "type": "PRICE_VOLUME_SPIKE",
                "symbol": symbol,
                "price_change_pct": round(price_change_pct, 2),
                "volume_change_pct": round(volume_change_pct, 2),
                "oldest_price": oldest_price,
                "newest_price": newest_price,
                "oldest_volume": oldest_volume,
                "newest_volume": newest_volume,
            })

        return alerts