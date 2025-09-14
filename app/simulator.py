import pandas as pd
from datetime import datetime
from typing import Dict, Any
from config import TRADE_LOGS_DIR
import os

class TradeSimulator:
    """
    Simulates trades internally and records results (WIN/LOSS).
    """

    def __init__(self):
        self.trade_history = []
        self.open_positions = {}

    def execute_trade(self, signal: Dict[str, Any], shared_state: Dict[str, Any]):
        """
        Execute a simulated trade based on the signal.
        """
        action = signal.get('action')
        price = signal.get('price', 0)
        confidence = signal.get('confidence', 0)
        reason = signal.get('reason', '')

        if action not in ['BUY', 'SELL']:
            return

        # For simplicity, we'll use a fixed position size
        position_size = 0.1  # 10% of balance
        balance = shared_state.get('balance', 10000)
        amount = balance * position_size / price if price > 0 else 0

        # Create trade record
        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trade_record = {
            'id': trade_id,
            'action': action,
            'price': price,
            'amount': amount,
            'timestamp': datetime.now(),
            'reason': reason,
            'confidence': confidence,
            'status': 'OPEN'
        }

        # Update shared state
        if 'positions' not in shared_state:
            shared_state['positions'] = {}
        shared_state['positions'][trade_id] = trade_record

        # Add to history
        self.trade_history.append(trade_record)
        shared_state['trade_history'] = self.trade_history

        # Save to log
        self._save_trade_log(trade_record)

        print(f"Executed {action} trade {trade_id} at ${price:.2f}")

    def close_trade(self, trade_id: str, close_price: float, shared_state: Dict[str, Any]):
        """
        Close a simulated trade and calculate P&L.
        """
        if trade_id not in shared_state.get('positions', {}):
            return

        trade = shared_state['positions'][trade_id]
        open_price = trade['price']
        amount = trade['amount']

        # Calculate P&L
        if trade['action'] == 'BUY':
            pnl = amount * (close_price - open_price)
        else:  # SELL
            pnl = amount * (open_price - close_price)

        # Update trade record
        trade['close_price'] = close_price
        trade['pnl'] = pnl
        trade['close_time'] = datetime.now()
        trade['status'] = 'WIN' if pnl > 0 else 'LOSS'

        # Update balance
        shared_state['balance'] += pnl

        # Remove from open positions
        del shared_state['positions'][trade_id]

        # Update history
        for i, t in enumerate(self.trade_history):
            if t['id'] == trade_id:
                self.trade_history[i] = trade
                break

        # Save to log
        self._save_trade_log(trade)

        print(f"Closed trade {trade_id}, P&L: ${pnl:.2f}")

    def _save_trade_log(self, trade: Dict[str, Any]):
        """Save trade to CSV log file."""
        log_file = f"{TRADE_LOGS_DIR}/trades_{datetime.now().strftime('%Y%m%d')}.csv"

        # Convert trade dict to DataFrame
        trade_df = pd.DataFrame([trade])

        # Append to existing file or create new
        if os.path.exists(log_file):
            existing_df = pd.read_csv(log_file)
            trade_df = pd.concat([existing_df, trade_df], ignore_index=True)

        trade_df.to_csv(log_file, index=False)

    def simulate_trade(self, symbol: str, timeframe: str = "15") -> str:
        """
        Dummy trade simulation for chatbot testing.
        """
        dummy_signal = {
            'action': 'BUY',
            'price': 27000,
            'confidence': 0.82,
            'reason': 'MACD crossover + bullish engulfing'
        }
        shared_state = {'balance': 10000}
        self.execute_trade(dummy_signal, shared_state)
        self.close_trade(list(shared_state['positions'].keys())[0], 27300, shared_state)
        trade = shared_state['trade_history'][0]
        return f"Simulated trade result: {trade['status']} (${trade['pnl']:.2f})"

