# app/signals/spike_detector.py

class SpikeDetector:
    def __init__(self, volume_spike_pct=20, price_spike_pct=1.0):
        self.previous_quotes = {}
        self.volume_spike_pct = volume_spike_pct
        self.price_spike_pct = price_spike_pct

    def check(self, quote):
        symbol = quote["symbol"]
        current_volume = quote.get("volume")
        current_price = quote.get("last")

        previous = self.previous_quotes.get(symbol)

        # Always store latest quote
        self.previous_quotes[symbol] = quote

        # First quote has nothing to compare against
        if not previous:
            return []

        alerts = []

        previous_volume = previous.get("volume")
        previous_price = previous.get("last")

        if previous_volume and current_volume:
            volume_change_pct = ((current_volume - previous_volume) / previous_volume) * 100

            if volume_change_pct >= self.volume_spike_pct:
                alerts.append({
                    "type": "VOLUME_SPIKE",
                    "symbol": symbol,
                    "previous_volume": previous_volume,
                    "current_volume": current_volume,
                    "change_pct": round(volume_change_pct, 2),
                })

        if previous_price and current_price:
            price_change_pct = ((current_price - previous_price) / previous_price) * 100

            if abs(price_change_pct) >= self.price_spike_pct:
                alerts.append({
                    "type": "PRICE_SPIKE",
                    "symbol": symbol,
                    "previous_price": previous_price,
                    "current_price": current_price,
                    "change_pct": round(price_change_pct, 2),
                })

        return alerts
