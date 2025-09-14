# app/strategy_selector.py

from typing import Dict, Any

class StrategySelector:
    """
    Selects the most suitable trading strategy based on market conditions.
    """

    def __init__(self):
        self.strategies = {
            0: "Trend Following",
            1: "Mean Reversion",
            2: "Breakout",
            3: "Scalping",
            4: "Swing Trading",
            5: "Arbitrage"
        }

        # Strategy suitability matrix (market condition -> suitable strategies)
        self.suitability_matrix = {
            "Strong Uptrend": [0, 2, 4],
            "Weak Uptrend": [0, 4],
            "Sideways/Breakout": [1, 2],
            "Weak Downtrend": [0, 4],
            "Strong Downtrend": [0, 2, 4],
            "High Volatility": [3, 2],
            "Low Volatility": [1, 3],
            "Reversal Potential": [1, 4],
            "Unknown": [4]
        }

    def select_strategy(self, market_condition: Dict[str, Any], indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the best trading strategy for current market conditions.

        Parameters:
        - market_condition: Dictionary with 'condition' and 'confidence' (e.g. {"condition": "High Volatility", "confidence": 0.82})
        - indicators: Dictionary with any indicator-related data (not used in basic version, placeholder for future use)

        Returns:
        - Dictionary with selected strategy name, code, and confidence level
        """
        condition = market_condition.get("condition", "Unknown")
        confidence = market_condition.get("confidence", 0.5)

        suitable_strategies = self.suitability_matrix.get(condition, [4])
        strategy_code = suitable_strategies[0]
        strategy_name = self.strategies.get(strategy_code, "Swing Trading")

        strategy_confidence = round(confidence * 0.9, 2)

        return {
            "strategy": strategy_name,
            "code": strategy_code,
            "confidence": strategy_confidence
        }

