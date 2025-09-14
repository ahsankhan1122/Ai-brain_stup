import numpy as np
from typing import Dict, Any, List

class RLScorer:
    """
    Uses reinforcement learning to score and adapt based on past trade outcomes.
    """
    
    def __init__(self):
        self.q_table = {}  # Simplified Q-table for strategy evaluation
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.strategy_rewards = {}
        
    def update_scores(self, shared_state: Dict[str, Any]):
        """
        Update strategy scores based on recent trade outcomes.
        """
        positions = shared_state.get('positions', {})
        trade_history = shared_state.get('trade_history', [])
        
        # Get recently closed trades
        recent_trades = [t for t in trade_history if 'pnl' in t]
        
        for trade in recent_trades:
            strategy = trade.get('strategy', 'Unknown')
            pnl = trade.get('pnl', 0)
            
            # Update strategy rewards
            if strategy not in self.strategy_rewards:
                self.strategy_rewards[strategy] = []
            
            self.strategy_rewards[strategy].append(pnl)
            
            # Simplified Q-learning update
            market_condition = shared_state.get('market_condition', {}).get('condition', 'Unknown')
            state = f"{market_condition}_{strategy}"
            
            if state not in self.q_table:
                self.q_table[state] = 0
            
            # Update Q-value
            self.q_table[state] = (1 - self.learning_rate) * self.q_table[state] + \
                                 self.learning_rate * pnl
        
        # Update strategy performance in shared state
        strategy_performance = {}
        for strategy, rewards in self.strategy_rewards.items():
            if rewards:
                strategy_performance[strategy] = {
                    'avg_profit': np.mean(rewards),
                    'win_rate': len([r for r in rewards if r > 0]) / len(rewards) if rewards else 0,
                    'total_trades': len(rewards)
                }
        
        shared_state['strategy_performance'] = strategy_performance
        
    def get_best_strategy(self, market_condition: str) -> str:
        """
        Get the best strategy for the current market condition based on RL.
        """
        best_strategy = "Swing Trading"  # Default
        best_value = -float('inf')
        
        # Check all strategies for this market condition
        for strategy in ["Trend Following", "Mean Reversion", "Breakout", 
                        "Scalping", "Swing Trading", "Arbitrage"]:
            state = f"{market_condition}_{strategy}"
            value = self.q_table.get(state, 0)
            
            if value > best_value:
                best_value = value
                best_strategy = strategy
        
        return best_strategy
