import pandas as pd
import numpy as np
from typing import Tuple

class TradingStrategy:
    def __init__(self, rsi_overbought: float = 70, rsi_oversold: float = 30):
        """
        Initialize trading strategy with parameters
        
        Args:
            rsi_overbought (float): RSI level considered overbought
            rsi_oversold (float): RSI level considered oversold
        """
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on technical indicators
        
        Args:
            data (pd.DataFrame): DataFrame with technical indicators
            
        Returns:
            pd.DataFrame: DataFrame with trading signals
        """
        df = data.copy()
        
        # Initialize signals
        df['Signal'] = 0
        
        # Generate signals based on RSI
        df.loc[df['RSI'] < self.rsi_oversold, 'Signal'] = 1  # Buy signal
        df.loc[df['RSI'] > self.rsi_overbought, 'Signal'] = -1  # Sell signal
        
        # Add MACD crossover signals
        df.loc[(df['MACD'] > df['Signal_Line']) & 
               (df['MACD'].shift(1) <= df['Signal_Line'].shift(1)), 'Signal'] = 1
        df.loc[(df['MACD'] < df['Signal_Line']) & 
               (df['MACD'].shift(1) >= df['Signal_Line'].shift(1)), 'Signal'] = -1
        
        # Add SMA crossover signals
        df.loc[(df['SMA_20'] > df['SMA_50']) & 
               (df['SMA_20'].shift(1) <= df['SMA_50'].shift(1)), 'Signal'] = 1
        df.loc[(df['SMA_20'] < df['SMA_50']) & 
               (df['SMA_20'].shift(1) >= df['SMA_50'].shift(1)), 'Signal'] = -1
        
        return df
    
    def calculate_position_sizes(self, signals: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
        """
        Calculate position sizes based on signals and capital
        
        Args:
            signals (pd.DataFrame): DataFrame with trading signals
            initial_capital (float): Initial capital for trading
            
        Returns:
            pd.DataFrame: DataFrame with position sizes
        """
        df = signals.copy()
        df['Position'] = 0
        
        # Simple position sizing: Invest all capital when signal is generated
        current_position = 0
        for i in range(len(df)):
            if df['Signal'].iloc[i] == 1 and current_position == 0:  # Buy
                current_position = initial_capital / df['close'].iloc[i]  # Using lowercase 'close'
            elif df['Signal'].iloc[i] == -1 and current_position > 0:  # Sell
                current_position = 0
            df['Position'].iloc[i] = current_position
            
        return df
    
    def calculate_returns(self, positions: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """
        Calculate strategy returns
        
        Args:
            positions (pd.DataFrame): DataFrame with positions
            
        Returns:
            Tuple[pd.DataFrame, float]: DataFrame with returns and total return
        """
        df = positions.copy()
        
        # Calculate daily returns using lowercase 'close'
        df['Returns'] = df['Position'].shift(1) * df['close'].pct_change()
        
        # Calculate cumulative returns
        df['Cumulative_Returns'] = (1 + df['Returns']).cumprod()
        
        # Calculate total return
        total_return = df['Cumulative_Returns'].iloc[-1] - 1 if len(df) > 0 else 0
        
        return df, total_return 