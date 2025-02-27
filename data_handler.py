from typing import Optional
import pandas as pd
import time
from yahoo_api import YahooFinanceAPI

class DataHandler:
    def __init__(self):
        self.data = None
        self.api = YahooFinanceAPI()
        
    def fetch_data(self, symbol: str, start_date: str, end_date: str, interval: str = '1d', max_retries: int = 3) -> pd.DataFrame:
        """
        Fetch historical data from Yahoo Finance with retries
        
        Args:
            symbol (str): Stock symbol
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            interval (str): Data interval (1d, 1h, etc.)
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            pd.DataFrame: Historical price data
        """
        for attempt in range(max_retries):
            try:
                # Use our custom API implementation
                self.data = self.api.get_stock_data(symbol, start_date, end_date, interval)
                
                if self.data is not None and not self.data.empty:
                    print(f"Successfully fetched data for {symbol}")
                    return self.data
                    
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print("Retrying after 2 seconds...")
                    time.sleep(2)
                continue
                
        print(f"Failed to fetch data for {symbol} after {max_retries} attempts")
        return pd.DataFrame()
    
    def add_technical_indicators(self, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Add technical indicators to the dataset
        
        Args:
            data (pd.DataFrame, optional): Input DataFrame. If None, uses self.data
            
        Returns:
            pd.DataFrame: DataFrame with technical indicators
        """
        df = data if data is not None else self.data
        if df is None or df.empty:
            return pd.DataFrame()
            
        try:
            # Calculate technical indicators
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_50'] = df['close'].rolling(window=50).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
        except Exception as e:
            print(f"Error calculating technical indicators: {str(e)}")
            return pd.DataFrame()
            
        return df
    
    def prepare_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch and prepare data with technical indicators
        
        Args:
            symbol (str): Stock symbol
            start_date (str): Start date
            end_date (str): End date
            
        Returns:
            pd.DataFrame: Prepared dataset with technical indicators
        """
        data = self.fetch_data(symbol, start_date, end_date)
        if not data.empty:
            data = self.add_technical_indicators(data)
            if not data.empty:
                # Remove any NaN values that might have been created
                data = data.dropna()
                return data
        return pd.DataFrame() 