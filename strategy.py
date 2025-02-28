import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict

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

    def add_technical_indicators(self, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        df = data if data is not None else self.data
        if df is None or df.empty:
            return pd.DataFrame()
        
        try:
            # Calculate required SMAs
            df['SMA_30'] = df['close'].rolling(window=30).mean()
            df['SMA_60'] = df['close'].rolling(window=60).mean()
            df['SMA_120'] = df['close'].rolling(window=120).mean()
            df['SMA_200'] = df['close'].rolling(window=200).mean()
            
            # Keep other indicators...
            
        except Exception as e:
            print(f"Error calculating technical indicators: {str(e)}")
            return pd.DataFrame()
        
        return df 

class LeveragedETFStrategy:
    def __init__(self, transaction_cost: float = 0.001, slippage: float = 0.001):
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        
    def generate_signals(self, data: pd.DataFrame, benchmark_data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['Signal'] = 0
        
        # Check if price is above all SMAs
        above_all_smas = (
            (df['close'] > df['SMA_30']) &
            (df['close'] > df['SMA_60']) &
            (df['close'] > df['SMA_120']) &
            (df['close'] > df['SMA_200'])
        )
        
        # Generate signals (1 for leveraged ETF, -1 for SHY)
        df.loc[above_all_smas, 'Signal'] = 1  # Buy leveraged ETF
        df.loc[~above_all_smas, 'Signal'] = -1  # Switch to SHY
        
        return df
        
    def calculate_position_sizes(self, signals: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
        df = signals.copy()
        df['Position'] = 0
        df['Transaction_Cost'] = 0
        
        current_position = 0
        for i in range(len(df)):
            if df['Signal'].iloc[i] != 0:
                # Calculate transaction costs and slippage
                if current_position != 0:
                    cost = abs(current_position * df['close'].iloc[i] * 
                             (self.transaction_cost + self.slippage))
                    df.loc[df.index[i], 'Transaction_Cost'] = cost
                    initial_capital -= cost
                
                # Update position
                if df['Signal'].iloc[i] == 1:
                    current_position = initial_capital / df['close'].iloc[i]
                else:
                    current_position = 0
                    
            df['Position'].iloc[i] = current_position
            
        return df 

class SMAStrategy:
    def __init__(self, transaction_cost: float = 0.001, slippage: float = 0.001):
        self.transaction_cost = transaction_cost
        self.slippage = slippage
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Initialize columns with proper dtypes
        df['Signal'] = 0
        df['Position'] = 0.0
        df['Asset'] = 'CASH'
        
        # Check if price is above all SMAs
        above_all_smas = (
            (df['close'] > df['SMA_30']) & 
            (df['close'] > df['SMA_60']) & 
            (df['close'] > df['SMA_120']) & 
            (df['close'] > df['SMA_200'])
        )
        
        # Generate signals (1 for UPRO, -1 for SHY)
        df.loc[above_all_smas, 'Signal'] = 1
        df.loc[~above_all_smas, 'Signal'] = -1
        
        return df
    
    def calculate_position_sizes(self, signals: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
        df = signals.copy()
        current_capital = float(initial_capital)
        current_asset = 'CASH'
        
        df['Position'] = 0.0
        df['Capital'] = float(initial_capital)
        df['Transaction_Costs'] = 0.0
        df['Asset'] = 'CASH'
        
        for i in range(len(df)):
            new_asset = 'UPRO' if df['Signal'].iloc[i] == 1 else 'SHY'
            
            # Only trade if we're changing assets
            if new_asset != current_asset:
                # Apply transaction costs
                if current_asset != 'CASH':
                    costs = current_capital * (self.transaction_cost + self.slippage)
                    current_capital -= costs
                    df.loc[df.index[i], 'Transaction_Costs'] = costs
                
                # Update position and capital
                df.loc[df.index[i], 'Position'] = current_capital / df['close'].iloc[i]
                df.loc[df.index[i], 'Capital'] = current_capital
                current_asset = new_asset
            else:
                # Maintain previous position
                df.loc[df.index[i], 'Position'] = df['Position'].iloc[i-1] if i > 0 else 0
                df.loc[df.index[i], 'Capital'] = current_capital
            
            df.loc[df.index[i], 'Asset'] = current_asset
        
        return df
    
    def calculate_returns(self, positions: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        df = positions.copy()
        df['Returns'] = 0.0
        
        # Calculate returns for each asset type
        for i in range(1, len(df)):
            if df['Asset'].iloc[i] == 'UPRO':
                # Calculate base return
                base_return = df['close'].pct_change().iloc[i]
                # Apply leverage without compounding the leverage effect
                df.loc[df.index[i], 'Returns'] = np.clip(base_return * 3, -0.3, 0.3)
            elif df['Asset'].iloc[i] == 'SHY':
                df.loc[df.index[i], 'Returns'] = (1 + 0.02) ** (1/252) - 1
        
        # Subtract transaction costs
        df['Returns'] -= df['Transaction_Costs'] / df['Capital'].shift(1)
        
        # Calculate cumulative returns
        df['Returns'] = df['Returns'].fillna(0)
        df['Cumulative_Returns'] = (1 + df['Returns']).cumprod()
        
        total_return = df['Cumulative_Returns'].iloc[-1] - 1 if len(df) > 0 else 0
        
        return df, total_return