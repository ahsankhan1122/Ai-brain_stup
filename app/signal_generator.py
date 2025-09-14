import pandas as pd
from typing import Dict, Any, List

class SignalGenerator:
    """
    Generates BUY/SELL signals based on selected strategy and market conditions.
    """
    
    def __init__(self):
        self.min_confidence = 0.6  # Minimum confidence threshold for signals
    
    def generate_signals(self, strategy: Dict[str, Any], df: pd.DataFrame, 
                        indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on the selected strategy.
        """
        signals = []
        strategy_code = strategy.get("code", 4)  # Default to Swing Trading
        strategy_confidence = strategy.get("confidence", 0.5)
        
        # Get current price and indicators
        current_price = df['close'].iloc[-1]
        current_indicators = indicators.get('current', {})
        
        # Generate signals based on strategy
        if strategy_code == 0:  # Trend Following
            signals.extend(self._trend_following_signals(df, current_indicators, strategy_confidence))
        elif strategy_code == 1:  # Mean Reversion
            signals.extend(self._mean_reversion_signals(df, current_indicators, strategy_confidence))
        elif strategy_code == 2:  # Breakout
            signals.extend(self._breakout_signals(df, current_indicators, strategy_confidence))
        elif strategy_code == 3:  # Scalping
            signals.extend(self._scalping_signals(df, current_indicators, strategy_confidence))
        else:  # Swing Trading (default)
            signals.extend(self._swing_trading_signals(df, current_indicators, strategy_confidence))
        
        # Filter signals by confidence
        signals = [s for s in signals if s.get('confidence', 0) >= self.min_confidence]
        
        return signals
    
    def _trend_following_signals(self, df: pd.DataFrame, indicators: Dict[str, Any], 
                               base_confidence: float) -> List[Dict[str, Any]]:
        """Generate trend following signals."""
        signals = []
        
        # Simple EMA crossover strategy
        if len(df) >= 50:
            ema_20 = indicators.get('ema_20', 0)
            ema_50 = indicators.get('ema_50', 0)
            prev_ema_20 = df['close'].iloc[-2]  # Simplified
            prev_ema_50 = df['close'].iloc[-3]  # Simplified
            
            if ema_20 > ema_50 and prev_ema_20 <= prev_ema_50:
                signals.append({
                    'action': 'BUY',
                    'confidence': base_confidence * 0.9,
                    'reason': 'EMA 20 crossed above EMA 50',
                    'price': df['close'].iloc[-1]
                })
            elif ema_20 < ema_50 and prev_ema_20 >= prev_ema_50:
                signals.append({
                    'action': 'SELL',
                    'confidence': base_confidence * 0.9,
                    'reason': 'EMA 20 crossed below EMA 50',
                    'price': df['close'].iloc[-1]
                })
        
        return signals
    
    def _mean_reversion_signals(self, df: pd.DataFrame, indicators: Dict[str, Any],
                              base_confidence: float) -> List[Dict[str, Any]]:
        """Generate mean reversion signals."""
        signals = []
        rsi = indicators.get('rsi', 50)
        
        # RSI-based mean reversion
        if rsi > 70:
            signals.append({
                'action': 'SELL',
                'confidence': base_confidence * (rsi - 70) / 30,
                'reason': f'RSI is overbought ({rsi:.2f})',
                'price': df['close'].iloc[-1]
            })
        elif rsi < 30:
            signals.append({
                'action': 'BUY',
                'confidence': base_confidence * (30 - rsi) / 30,
                'reason': f'RSI is oversold ({rsi:.2f})',
                'price': df['close'].iloc[-1]
            })
        
        return signals
    
    def _breakout_signals(self, df: pd.DataFrame, indicators: Dict[str, Any],
                        base_confidence: float) -> List[Dict[str, Any]]:
        """Generate breakout signals."""
        signals = []
        
        # Simplified breakout detection
        if len(df) >= 20:
            current_high = df['high'].iloc[-1]
            recent_high = df['high'].iloc[-20:-1].max()
            
            current_low = df['low'].iloc[-1]
            recent_low = df['low'].iloc[-20:-1].min()
            
            if current_high > recent_high:
                signals.append({
                    'action': 'BUY',
                    'confidence': base_confidence * 0.8,
                    'reason': 'Price broke above recent resistance',
                    'price': df['close'].iloc[-1]
                })
            elif current_low < recent_low:
                signals.append({
                    'action': 'SELL',
                    'confidence': base_confidence * 0.8,
                    'reason': 'Price broke below recent support',
                    'price': df['close'].iloc[-1]
                })
        
        return signals
    
    def _scalping_signals(self, df: pd.DataFrame, indicators: Dict[str, Any],
                        base_confidence: float) -> List[Dict[str, Any]]:
        """Generate scalping signals."""
        # This would typically be more complex with order book analysis
        # For now, return empty list
        return []
    
    def _swing_trading_signals(self, df: pd.DataFrame, indicators: Dict[str, Any],
                             base_confidence: float) -> List[Dict[str, Any]]:
        """Generate swing trading signals (combination of strategies)."""
        signals = []
        signals.extend(self._trend_following_signals(df, indicators, base_confidence))
        signals.extend(self._mean_reversion_signals(df, indicators, base_confidence))
        signals.extend(self._breakout_signals(df, indicators, base_confidence))
        return signals
