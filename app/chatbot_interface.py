from app.llm_explainer import LLMExplainer
from app.pattern_detector import PatternDetector
from app.strategy_selector import StrategySelector
from app.market_classifier import MarketClassifier

# Safe imports
try:
    from app.simulator import Simulator
except ImportError:
    Simulator = None

try:
    from app.collector import Collector
except ImportError:
    Collector = None


class TradingChatbot:
    """
    Smart trading assistant that routes queries to intelligent modules
    like pattern detection, strategy suggestion, simulator, LLM, etc.
    """

    def __init__(self, shared_state=None):
        self.shared_state = shared_state or {}

        # Core ML Modules
        self.llm = LLMExplainer()
        self.pattern_detector = PatternDetector()
        self.strategy_selector = StrategySelector()
        self.market_classifier = MarketClassifier()

        # Optional modules
        self.simulator = Simulator() if Simulator else None
        self.collector = Collector(shared_state=self.shared_state) if Collector else None

    def respond(self, user_input: str) -> str:
        """
        Route user input to the correct module based on natural language intent.
        """
        try:
            query = user_input.lower()

            # === Coin Price Check (any coin) ===
            price_keywords = ["price", "current price", "rate", "quote", "latest", "symbol"]
            if any(word in query for word in price_keywords):
                if self.collector:
                    return self.collector.get_price_info(query)
                return "⚠️ Price collector module not available."

            # === Market Trend Analysis ===
            trend_keywords = ["trend", "direction", "market trend", "bullish", "bearish"]
            if any(word in query for word in trend_keywords):
                return self.market_classifier.classify_market(self.shared_state)

            # === Pattern Detection ===
            pattern_keywords = ["pattern", "candlestick", "formation"]
            if any(word in query for word in pattern_keywords):
                return self.pattern_detector.detect_latest(self.shared_state)

            # === Strategy Suggestions ===
            strategy_keywords = ["strategy", "plan", "approach", "best way", "entry", "exit"]
            if any(word in query for word in strategy_keywords):
                return self.strategy_selector.select_strategy(self.shared_state)

            # === Simulation / Backtest ===
            if "simulate" in query or "backtest" in query:
                if self.simulator:
                    return self.simulator.run_backtest(self.shared_state)
                return "⚠️ Simulation module not available."

            # === Default fallback to LLM ===
            return self.llm.chat(user_input)

        except Exception as e:
            return f"[Chatbot Error] {e}"

