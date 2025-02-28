import pandas as pd
import numpy as np
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns

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
        returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Basic metrics with safety checks
        total_return = min(self.results['Cumulative_Returns'].iloc[-1] - 1, 1e6)
        annual_return = min((1 + total_return) ** (252 / len(returns)) - 1, 1e6)
        
        # Risk metrics
        daily_std = returns.std()
        annualized_std = min(daily_std * np.sqrt(252), 1e6)
        sharpe_ratio = (annual_return - 0.02) / annualized_std if annualized_std != 0 else 0
        
        # Drawdown analysis with safety checks
        cumulative_returns = self.results['Cumulative_Returns'].clip(upper=1e6)
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns / rolling_max - 1).clip(lower=-0.99)
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
    
    def plot_results(self, benchmark_data: pd.DataFrame = None):
        """
        Plot strategy performance results
        
        Args:
            benchmark_data (pd.DataFrame, optional): Benchmark data for comparison
        """
        if self.results is None:
            print("No results to plot. Run backtest first.")
            return
            
        # Use a built-in matplotlib style instead
        plt.style.use('fivethirtyeight')  # or 'ggplot'
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 16))
        
        # Plot 1: Cumulative Returns
        self.results['Cumulative_Returns'].plot(ax=ax1, label='Strategy')
        if benchmark_data is not None:
            benchmark_returns = (1 + benchmark_data['close'].pct_change()).cumprod()
            benchmark_returns.plot(ax=ax1, label='Benchmark (SPY)')
        ax1.set_title('Cumulative Returns')
        ax1.set_ylabel('Returns')
        ax1.legend()
        ax1.grid(True)
        
        # Plot 2: Drawdowns
        rolling_max = self.results['Cumulative_Returns'].expanding().max()
        drawdowns = (self.results['Cumulative_Returns'] / rolling_max - 1)
        drawdowns.plot(ax=ax2)
        ax2.set_title('Strategy Drawdowns')
        ax2.set_ylabel('Drawdown')
        ax2.grid(True)
        
        # Plot 3: Asset Allocation
        asset_allocation = pd.DataFrame({
            'Asset': self.results['Asset'],
            'Date': self.results.index
        })
        sns.scatterplot(data=asset_allocation, x='Date', y='Asset', ax=ax3)
        ax3.set_title('Asset Allocation Over Time')
        ax3.grid(True)
        
        plt.tight_layout()
        plt.show()
        
        # Additional performance visualization
        self._plot_monthly_returns()
        self._plot_rolling_metrics()
    
    def _plot_monthly_returns(self):
        """Plot monthly returns heatmap"""
        if self.results is None:
            return
            
        # Calculate monthly returns
        monthly_returns = self.results['Returns'].resample('M').agg(lambda x: (1 + x).prod() - 1)
        monthly_returns_table = monthly_returns.groupby([monthly_returns.index.year, 
                                                       monthly_returns.index.month]).first()
        monthly_returns_table = monthly_returns_table.unstack()
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(monthly_returns_table, 
                   annot=True, 
                   fmt='.2%', 
                   center=0,
                   cmap='RdYlGn',
                   cbar_kws={'label': 'Monthly Returns'})
        plt.title('Monthly Returns Heatmap')
        plt.xlabel('Month')
        plt.ylabel('Year')
        plt.show()
    
    def _plot_rolling_metrics(self):
        """Plot rolling Sharpe ratio and volatility"""
        if self.results is None:
            return
            
        # Calculate rolling metrics
        window = 252  # One year trading days
        rolling_returns = self.results['Returns'].rolling(window=window)
        rolling_std = rolling_returns.std() * np.sqrt(252)
        rolling_sharpe = (rolling_returns.mean() * 252 - 0.02) / rolling_std
        
        # Plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        rolling_sharpe.plot(ax=ax1)
        ax1.set_title('Rolling Sharpe Ratio (1-Year Window)')
        ax1.grid(True)
        
        rolling_std.plot(ax=ax2)
        ax2.set_title('Rolling Volatility (1-Year Window)')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def compare_to_benchmark(self, benchmark_data: pd.DataFrame) -> Dict[str, Any]:
        """Compare strategy performance to benchmark (SPY)"""
        strategy_returns = self.results['Returns']
        benchmark_returns = benchmark_data['close'].pct_change()
        
        # Calculate comparative metrics
        excess_returns = strategy_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = (excess_returns.mean() * 252) / tracking_error
        
        beta = strategy_returns.cov(benchmark_returns) / benchmark_returns.var()
        
        metrics = {
            'Excess Returns': excess_returns.mean() * 252,
            'Tracking Error': tracking_error,
            'Information Ratio': information_ratio,
            'Beta': beta
        }
        
        return metrics
    
    def run_with_benchmark(self, benchmark_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run backtest with benchmark comparison
        """
        # Run regular backtest
        metrics = self.run()
        
        # Calculate benchmark returns
        benchmark_returns = benchmark_data['close'].pct_change()
        strategy_returns = self.results['Returns']
        
        # Calculate comparative metrics
        excess_returns = strategy_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = (excess_returns.mean() * 252) / tracking_error
        
        # Add benchmark metrics
        metrics.update({
            'Excess Returns': excess_returns.mean() * 252,
            'Tracking Error': tracking_error,
            'Information Ratio': information_ratio,
            'Beta': strategy_returns.cov(benchmark_returns) / benchmark_returns.var()
        })
        
        return metrics

class SMAStrategy:
    def __init__(self, transaction_cost: float = 0.001, slippage: float = 0.001):
        self.transaction_cost = transaction_cost
        self.slippage = slippage
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['Signal'] = 0
        
        # Check if price is above all SMAs
        df['Above_All_SMAs'] = (
            (df['close'] > df['SMA_30']) &
            (df['close'] > df['SMA_60']) &
            (df['close'] > df['SMA_120']) &
            (df['close'] > df['SMA_200'])
        )
        
        # Generate signals only when the condition changes
        df['Signal'] = df['Above_All_SMAs'].astype(int).diff()
        
        return df

    def calculate_position_sizes(self, signals: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
        df = signals.copy()
        df['Position'] = 0.0
        df['Asset'] = 'CASH'
        df['Capital'] = float(initial_capital)
        df['Transaction_Costs'] = 0.0
        
        current_capital = float(initial_capital)
        
        for i in range(len(df)):
            if df['Above_All_SMAs'].iloc[i]:
                # Buy/Hold UPRO
                if df['Asset'].iloc[i-1] != 'UPRO' and i > 0:
                    # Calculate transaction costs
                    costs = current_capital * self.transaction_cost
                    current_capital -= costs
                    df.loc[df.index[i], 'Transaction_Costs'] = costs
                
                df.loc[df.index[i], 'Position'] = current_capital / df['close'].iloc[i]
                df.loc[df.index[i], 'Asset'] = 'UPRO'
            else:
                # Switch to SHY
                if df['Asset'].iloc[i-1] != 'SHY' and i > 0:
                    costs = current_capital * self.transaction_cost
                    current_capital -= costs
                    df.loc[df.index[i], 'Transaction_Costs'] = costs
                
                df.loc[df.index[i], 'Position'] = current_capital / df['close'].iloc[i]
                df.loc[df.index[i], 'Asset'] = 'SHY'
            
            df.loc[df.index[i], 'Capital'] = current_capital
        
        return df