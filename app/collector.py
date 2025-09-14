import time
import os
import pandas as pd
import requests

class Collector:
    """
    Collects live crypto price data from Binance public API
    and saves rolling candle data into CSV files.
    Also supports dynamic symbol lookup for chatbot queries.
    """
    def __init__(self, shared_state=None, symbols=None, intervals=None, data_dir="data"):
        self.shared_state = shared_state or {}
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT"]   # default pairs
        self.intervals = intervals or ["1m", "5m"]          # default timeframes
        self.data_dir = data_dir
        self.running = False
        self.all_symbols = self.fetch_all_symbols()

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_all_symbols(self):
        """Fetch all tradable USDT pairs dynamically from Binance."""
        try:
            url = "https://api.binance.com/api/v3/exchangeInfo"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            symbols = [s["symbol"] for s in data["symbols"] if s["quoteAsset"] == "USDT"]
            return symbols
        except Exception as e:
            print(f"[Collector] Error fetching symbol list: {e}")
            return []

    def fetch_candle(self, symbol, interval):
        """Fetch latest kline (candle) for a given symbol + interval."""
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": 1}
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()[0]
            candle = {
                "timestamp": pd.to_datetime(data[0], unit="ms"),
                "open": float(data[1]),
                "high": float(data[2]),
                "low": float(data[3]),
                "close": float(data[4]),
                "volume": float(data[5]),
            }
            return candle
        except Exception as e:
            print(f"[Collector] Error fetching {symbol} {interval}: {e}")
            return None

    def save_candle(self, symbol, interval, candle):
        """Save new candle into CSV (rolling window of last 200 rows)."""
        file_path = os.path.join(self.data_dir, f"{symbol}_{interval}.csv")

        if os.path.exists(file_path):
            df = pd.read_csv(file_path, parse_dates=["timestamp"])
        else:
            df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

        df = pd.concat([df, pd.DataFrame([candle])], ignore_index=True)
        df = df.tail(200)  # keep last 200 rows
        df.to_csv(file_path, index=False)

        print(f"[Collector] Saved {symbol} {interval} candle: {candle['close']}")

    def get_price_info(self, query: str) -> str:
        """
        Extract symbol dynamically from query and return current price.
        Example: "btc price", "what is eth doing"
        """
        query_lower = query.lower()
        # Try to match any USDT symbol that starts with first 3 letters (e.g. btc, eth, xrp)
        matched = [s for s in self.all_symbols if s.lower().startswith(query_lower[:3])]

        if not matched:
            return "⚠️ Could not recognize any supported coin in your question."

        symbol = matched[0]

        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            price = float(data["price"])
            return f"💰 Current price of {symbol} is ${price:.4f}"
        except Exception as e:
            return f"❌ Error fetching price for {symbol}: {e}"

    def start(self):
        """Main loop: fetch and save candles continuously."""
        self.running = True
        print("[Collector] Starting data collection...")

        while self.running:
            for symbol in self.symbols:
                for interval in self.intervals:
                    candle = self.fetch_candle(symbol, interval)
                    if candle:
                        self.save_candle(symbol, interval, candle)
                        self.shared_state[f"{symbol}_{interval}"] = candle

            time.sleep(60)  # wait until next minute

    def stop(self):
        self.running = False
        print("[Collector] Stopped.")


def run_collector(shared_state):
    """
    Entry point for main.py
    """
    collector = Collector(shared_state)
    collector.start()

