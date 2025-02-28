from data_handler import DataHandler
from strategy import TradingStrategy, SMAStrategy
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
        strategy = SMAStrategy(transaction_cost=0.001, slippage=0.001)
        
        # Set up backtest parameters
        symbols = ["UPRO", "SHY", "SPY"]  # UPRO is 3x leveraged S&P 500
        start_date = "2020-01-01"
        end_date = datetime.now().strftime("%Y-%m-%d")
        initial_capital = 100000
        
        # Fetch data for all symbols
        data = {}
        for symbol in symbols:
            data[symbol] = data_handler.prepare_data(symbol, start_date, end_date)
        
        # Run backtest
        backtester = Backtester(data["UPRO"], strategy, initial_capital)
        metrics = backtester.run_with_benchmark(data["SPY"])
        
        # Print results
        print_section("BACKTEST RESULTS")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.2%}")
        
        # Plot results
        print_section("GENERATING PLOTS")
        backtester.plot_results(benchmark_data=data["SPY"])
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise  # Add this to see the full traceback

if __name__ == "__main__":
    main()

