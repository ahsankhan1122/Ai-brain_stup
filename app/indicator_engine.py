import pandas as pd
import numpy as np
from typing import Dict, Any

class IndicatorEngine:
    """
    Calculates technical indicators from OHLCV data.
    """
    
    def __init__(self):
        self.indicators_history = {}
    
    def calculate_ema(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator."""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        upper_band = sma + (rolling_std * std_dev)
        lower_band = sma - (rolling_std * std_dev)
        
        return {
            'sma': sma,
            'upper_band': upper_band,
            'lower_band': lower_band
        }
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        return atr
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        indicators = {}
        
        # Moving averages
        indicators['ema_20'] = self.calculate_ema(df, 20)
        indicators['ema_50'] = self.calculate_ema(df, 50)
        
        # Oscillators
        indicators['rsi'] = self.calculate_rsi(df, 14)
        
        # MACD
        macd_data = self.calculate_macd(df)
        indicators.update(macd_data)
        
        # Bollinger Bands
        bb_data = self.calculate_bollinger_bands(df)
        indicators.update(bb_data)
        
        # Volatility
        indicators['atr'] = self.calculate_atr(df)
        
        # Add current values
        current_values = {}
        for key, value in indicators.items():
            if not value.empty:
                current_values[key] = value.iloc[-1]
        
        indicators['current'] = current_values
        return indicators
