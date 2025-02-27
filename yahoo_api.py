import requests
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
import time

class YahooFinanceAPI:
    BASE_URL = "https://query2.finance.yahoo.com/v8/finance/chart/"
    
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://finance.yahoo.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36'
        }
    
    def _convert_to_timestamp(self, date_str: str) -> int:
        """Convert date string to UNIX timestamp."""
        return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str, interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch stock data directly from Yahoo Finance API
        
        Args:
            symbol (str): Stock symbol
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            interval (str): Data interval (1d, 1h, 1m, etc.)
            
        Returns:
            Optional[pd.DataFrame]: DataFrame with stock data or None if failed
        """
        # Convert dates to timestamps
        period1 = self._convert_to_timestamp(start_date)
        period2 = self._convert_to_timestamp(end_date)
        
        # Construct URL
        params = {
            'period1': period1,
            'period2': period2,
            'interval': interval,
            'includePrePost': 'true',
            'events': 'div,split,earn',
            'lang': 'en-US',
            'region': 'US'
        }
        
        url = f"{self.BASE_URL}{symbol}"
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            
            # Check for errors in the response
            if data.get('error'):
                print(f"API Error: {data['error']}")
                return None
                
            # Extract relevant data
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quote_data = result['indicators']['quote'][0]
            
            # Create DataFrame
            df = pd.DataFrame({
                'timestamp': timestamps,
                'open': quote_data.get('open', []),
                'high': quote_data.get('high', []),
                'low': quote_data.get('low', []),
                'close': quote_data.get('close', []),
                'volume': quote_data.get('volume', [])
            })
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            
            # Remove rows with NaN values
            df = df.dropna()
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {str(e)}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Error parsing response: {str(e)}")
            return None
            
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock information including meta data
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict[str, Any]: Dictionary containing stock information
        """
        end_timestamp = int(time.time())
        start_timestamp = end_timestamp - 86400  # 24 hours ago
        
        params = {
            'period1': start_timestamp,
            'period2': end_timestamp,
            'interval': '1d'
        }
        
        try:
            response = requests.get(f"{self.BASE_URL}{symbol}", params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('error'):
                return {}
                
            meta = data['chart']['result'][0]['meta']
            
            return {
                'symbol': meta.get('symbol'),
                'currency': meta.get('currency'),
                'exchange': meta.get('exchangeName'),
                'full_exchange_name': meta.get('fullExchangeName'),
                'long_name': meta.get('longName'),
                'short_name': meta.get('shortName'),
                'regular_market_price': meta.get('regularMarketPrice'),
                'regular_market_time': meta.get('regularMarketTime'),
                'timezone': meta.get('timezone'),
                'fifty_two_week_high': meta.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': meta.get('fiftyTwoWeekLow')
            }
            
        except Exception as e:
            print(f"Error fetching stock info: {str(e)}")
            return {}

def test_api():
    """Test the YahooFinanceAPI functionality"""
    api = YahooFinanceAPI()
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    intervals = ['1d', '1h']
    
    print("Testing YahooFinanceAPI...")
    print("-" * 50)
    
    # Test stock info
    print("\nTesting get_stock_info():")
    for symbol in symbols:
        print(f"\nFetching info for {symbol}...")
        info = api.get_stock_info(symbol)
        if info:
            print(f"Success! {symbol} Info:")
            for key, value in info.items():
                print(f"{key}: {value}")
        else:
            print(f"Failed to fetch info for {symbol}")
    
    # Test historical data
    print("\nTesting get_stock_data():")
    for symbol in symbols:
        for interval in intervals:
            print(f"\nFetching {interval} data for {symbol}...")
            
            # Get data for last 30 days
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
            
            df = api.get_stock_data(symbol, start_date, end_date, interval)
            if df is not None and not df.empty:
                print(f"Success! Shape: {df.shape}")
                print("\nFirst few rows:")
                print(df.head())
                print("\nColumns:", df.columns.tolist())
            else:
                print(f"Failed to fetch data for {symbol}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_api() 