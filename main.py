from data_handler import DataHandler
from strategy import TradingStrategy
from backtester import Backtester
import matplotlib.pyplot as plt
import sys
from datetime import datetime

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*20} {title} {'='*20}")

def main():
    try:
        print_section("INITIALIZATION")
        print("Initializing components...")
        data_handler = DataHandler()
        strategy = TradingStrategy(rsi_overbought=70, rsi_oversold=30)
        
        # Set up backtest parameters
        symbol = "AAPL"  # Example stock
        start_date = "2020-01-01"
        end_date = datetime.now().strftime("%Y-%m-%d")  # Use current date
        initial_capital = 100000  # $100,000 initial capital
        
        print_section("BACKTEST CONFIGURATION")
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial capital: ${initial_capital:,.2f}")
        print(f"RSI Parameters: Overbought={strategy.rsi_overbought}, Oversold={strategy.rsi_oversold}")
        
        # Fetch and prepare data
        print_section("DATA FETCHING")
        print(f"Fetching data for {symbol}...")
        data = data_handler.prepare_data(symbol, start_date, end_date)
        
        if data.empty:
            print("\nError: No data available. Please check:")
            print("1. Your internet connection")
            print("2. The stock symbol")
            print("3. The date range")
            return
        
        print(f"Successfully loaded {len(data)} days of data")
        print("\nData Preview:")
        print(data.head())
        print("\nAvailable Indicators:", ", ".join(data.columns))
        
        # Initialize and run backtest
        print_section("RUNNING BACKTEST")
        backtester = Backtester(data, strategy, initial_capital)
        metrics = backtester.run()
        
        if not metrics:
            print("Error: Failed to calculate performance metrics")
            return
        
        # Print results
        print_section("BACKTEST RESULTS")
        for metric, value in metrics.items():
            if isinstance(value, float):
                if 'Return' in metric or 'Rate' in metric:
                    print(f"{metric}: {value:.2%}")
                else:
                    print(f"{metric}: {value:.4f}")
            else:
                print(f"{metric}: {value}")
        
        # Plot results
        print_section("GENERATING PLOTS")
        backtester.plot_results()
        print("\nBacktest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nBacktest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify the stock symbol exists")
        print("3. Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        print("4. Check the date range is valid")
        print("\nFull error details:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

