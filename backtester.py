import pandas as pd
import numpy as np
from typing import Dict, Any

class Backtester:
    def __init__(self, data: pd.DataFrame, strategy: Any, initial_capital: float = 100000):
        """
        Initialize backtester
        
        Args:
            data (pd.DataFrame): Historical price data with indicators
            strategy: Trading strategy instance
            initial_capital (float): Initial capital for backtesting
        """
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.results = None
        
    def run(self) -> Dict[str, Any]:
        """
        Run backtest and calculate performance metrics
        
        Returns:
            Dict[str, Any]: Dictionary containing performance metrics
        """
        # Generate trading signals
        signals = self.strategy.generate_signals(self.data)
        
        # Calculate positions and returns
        positions = self.strategy.calculate_position_sizes(signals, self.initial_capital)
        results, total_return = self.strategy.calculate_returns(positions)
        self.results = results
        
        # Calculate performance metrics
        metrics = self._calculate_metrics()
        
        return metrics
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """
        Calculate various performance metrics
        
        Returns:
            Dict[str, float]: Dictionary of performance metrics
        """
        if self.results is None or len(self.results) == 0:
            return {}
            
        returns = self.results['Returns'].dropna()
        
        # Basic metrics
        total_return = self.results['Cumulative_Returns'].iloc[-1] - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        
        # Risk metrics
        daily_std = returns.std()
        annualized_std = daily_std * np.sqrt(252)
        sharpe_ratio = (annual_return - 0.02) / annualized_std if annualized_std != 0 else 0
        
        # Drawdown analysis
        cumulative_returns = self.results['Cumulative_Returns']
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        # Trading metrics
        signals = self.results['Signal']
        total_trades = len(signals[signals != 0])
        winning_trades = len(returns[returns > 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        metrics = {
            'Total Return': total_return,
            'Annual Return': annual_return,
            'Annualized Volatility': annualized_std,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown,
            'Total Trades': total_trades,
            'Win Rate': win_rate
        }
        
        return metrics
    
    def plot_results(self) -> None:
        """
        Plot backtest results including cumulative returns and drawdowns
        """
        if self.results is None or len(self.results) == 0:
            print("No results to plot")
            return
            
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot cumulative returns
        self.results['Cumulative_Returns'].plot(ax=ax1)
        ax1.set_title('Cumulative Returns')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Returns')
        ax1.grid(True)
        
        # Plot drawdowns
        rolling_max = self.results['Cumulative_Returns'].expanding().max()
        drawdowns = self.results['Cumulative_Returns'] / rolling_max - 1
        drawdowns.plot(ax=ax2)
        ax2.set_title('Drawdowns')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Drawdown')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show() 