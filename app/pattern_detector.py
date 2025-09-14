import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, Any, List
from config import PATTERN_MODEL_PATH

class PatternDetector:
    """
    ML module for detecting candlestick and chart patterns.
    Uses pre-trained models from models/ directory.
    """

    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the pre-trained pattern recognition model."""
        try:
            self.model = joblib.load(PATTERN_MODEL_PATH)
            print(f"Loaded pattern model from {PATTERN_MODEL_PATH}")
        except FileNotFoundError:
            print(f"Model file {PATTERN_MODEL_PATH} not found. Using rule-based fallback.")
            self.model = None

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from OHLCV data for pattern recognition.
        """
        features = df.copy()
        features['body_size'] = abs(features['close'] - features['open'])
        features['upper_wick'] = features['high'] - features[['open', 'close']].max(axis=1)
        features['lower_wick'] = features[['open', 'close']].min(axis=1) - features['low']
        features['price_change'] = features['close'].pct_change()
        features['volume_change'] = features['volume'].pct_change()
        return features.dropna()

    def predict_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Predict candlestick patterns from the latest data.
        Returns pattern name and confidence.
        """
        patterns = []

        # Use ML model if available (TODO: implement when ready)
        if self.model is not None:
            try:
                features = self.extract_features(df.tail(5))
                # Replace this with real model inference
                pass
            except Exception as e:
                print(f"Error in model prediction: {e}")

        # Rule-based fallback
        if len(df) >= 3:
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            prev2 = df.iloc[-3]

            # Bullish Engulfing
            if (latest['close'] > latest['open'] and 
                prev['close'] < prev['open'] and 
                latest['open'] < prev['close'] and 
                latest['close'] > prev['open']):
                patterns.append({"pattern": "Bullish Engulfing", "confidence": 0.85})

            # Bearish Engulfing
            elif (latest['close'] < latest['open'] and 
                  prev['close'] > prev['open'] and 
                  latest['open'] > prev['close'] and 
                  latest['close'] < prev['open']):
                patterns.append({"pattern": "Bearish Engulfing", "confidence": 0.85})

            # Doji
            if abs(latest['close'] - latest['open']) / max((latest['high'] - latest['low']), 0.0001) < 0.1:
                patterns.append({"pattern": "Doji", "confidence": 0.75})

            # Hammer
            if (latest['close'] > latest['open'] and 
                (latest['close'] - latest['low']) > 2 * (latest['high'] - latest['close']) and
                (latest['open'] - latest['low']) > 2 * (latest['high'] - latest['open'])):
                patterns.append({"pattern": "Hammer", "confidence": 0.8})

        return patterns

    def detect(self, symbol: str, timeframe: str = "15") -> str:
        """
        Detect patterns from the latest CSV file for chatbot integration.
        """
        path = f"data/live_candles/{symbol}_{timeframe}_latest.csv"
        if not os.path.exists(path):
            return f"No data found for {symbol} ({timeframe}m)."

        try:
            df = pd.read_csv(path)
            if df.empty or len(df) < 5:
                return f"Not enough candle data to detect patterns."

            patterns = self.predict_patterns(df)

            if not patterns:
                return f"No strong pattern found in {symbol} ({timeframe}m)."
            else:
                results = [f"{p['pattern']} ({int(p['confidence']*100)}%)" for p in patterns]
                return f"{symbol} pattern(s) detected on {timeframe}m: " + ", ".join(results)

        except Exception as e:
            return f"Pattern detection error: {str(e)}"

