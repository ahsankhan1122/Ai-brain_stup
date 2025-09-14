import pandas as pd
import joblib
from typing import Dict, Any
from config import MARKET_MODEL_PATH

class MarketClassifier:
    """
    Classifies the current market condition into predefined types.
    """
    
    def __init__(self):
        self.model = None
        self.load_model()
        
        # Predefined market conditions
        self.market_conditions = {
            0: "Strong Uptrend",
            1: "Weak Uptrend",
            2: "Sideways/Breakout",
            3: "Weak Downtrend",
            4: "Strong Downtrend",
            5: "High Volatility",
            6: "Low Volatility",
            7: "Reversal Potential"
        }
    
    def load_model(self):
        """Load the pre-trained market classification model."""
        try:
            self.model = joblib.load(MARKET_MODEL_PATH)
            print(f"Loaded market model from {MARKET_MODEL_PATH}")
        except FileNotFoundError:
            print(f"Model file {MARKET_MODEL_PATH} not found. Using rule-based fallback.")
            self.model = None
    
    def extract_features(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> pd.DataFrame:
        """
        Extract features for market condition classification.
        """
        features = {}
        
        # Price trends
        features['price_change_1h'] = (df['close'].iloc[-1] - df['close'].iloc[-12]) / df['close'].iloc[-12] if len(df) >= 12 else 0
        features['price_change_4h'] = (df['close'].iloc[-1] - df['close'].iloc[-48]) / df['close'].iloc[-48] if len(df) >= 48 else 0
        features['price_change_24h'] = (df['close'].iloc[-1] - df['close'].iloc[-96]) / df['close'].iloc[-96] if len(df) >= 96 else 0
        
        # Indicator-based features
        if 'current' in indicators:
            current = indicators['current']
            features['rsi'] = current.get('rsi', 50)
            features['macd_histogram'] = current.get('histogram', 0)
            features['bollinger_position'] = (df['close'].iloc[-1] - current.get('lower_band', 0)) / (current.get('upper_band', 1) - current.get('lower_band', 1)) if current.get('upper_band', 0) != current.get('lower_band', 0) else 0.5
        
        # Volume features
        features['volume_change'] = df['volume'].pct_change().iloc[-1] if len(df) > 1 else 0
        features['volume_ratio'] = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1] if len(df) >= 20 else 1
        
        return pd.DataFrame([features])
    
    def classify_market(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the current market condition.
        """
        # Use ML model if available
        if self.model is not None:
            try:
                features = self.extract_features(df, indicators)
                prediction = self.model.predict(features)[0]
                confidence = np.max(self.model.predict_proba(features)[0])
                condition = self.market_conditions.get(prediction, "Unknown")
                
                return {
                    "condition": condition,
                    "confidence": confidence,
                    "code": prediction
                }
            except Exception as e:
                print(f"Error in market classification: {e}")
        
        # Fallback to rule-based classification
        return self.rule_based_classification(df, indicators)
    
    def rule_based_classification(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rule-based fallback for market classification.
        """
        if len(df) < 20:
            return {"condition": "Insufficient Data", "confidence": 0, "code": -1}
        
        current = indicators.get('current', {})
        rsi = current.get('rsi', 50)
        price_change_24h = (df['close'].iloc[-1] - df['close'].iloc[-96]) / df['close'].iloc[-96] if len(df) >= 96 else 0
        
        # Simple rule-based classification
        if price_change_24h > 0.05:
            condition = "Strong Uptrend"
            code = 0
            confidence = 0.8
        elif price_change_24h > 0.02:
            condition = "Weak Uptrend"
            code = 1
            confidence = 0.7
        elif price_change_24h < -0.05:
            condition = "Strong Downtrend"
            code = 4
            confidence = 0.8
        elif price_change_24h < -0.02:
            condition = "Weak Downtrend"
            code = 3
            confidence = 0.7
        elif abs(price_change_24h) < 0.01:
            condition = "Sideways/Breakout"
            code = 2
            confidence = 0.6
        else:
            condition = "Uncertain"
            code = -1
            confidence = 0.5
        
        # Adjust based on RSI
        if rsi > 70 and "Uptrend" in condition:
            condition += " (Overbought)"
            confidence *= 0.9
        elif rsi < 30 and "Downtrend" in condition:
            condition += " (Oversold)"
            confidence *= 0.9
        
        return {
            "condition": condition,
            "confidence": confidence,
            "code": code
        }
