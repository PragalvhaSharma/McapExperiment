# Market Capitalization Experiment (MCAP EXP)

A comprehensive stock market backtesting framework for developing, testing, and optimizing trading strategies based on technical indicators.

## Overview

This project provides a modular framework for backtesting trading strategies on historical stock data. It leverages the Yahoo Finance API for data retrieval and implements various technical indicators for signal generation.

## Features

- **Data Handling**: Fetch and process historical stock data from Yahoo Finance
- **Technical Indicators**: Calculate RSI, MACD, Moving Averages, and more
- **Strategy Development**: Implement and test custom trading strategies
- **Backtesting Engine**: Evaluate strategy performance with historical data
- **Performance Metrics**: Calculate key metrics like Sharpe ratio, drawdown, and returns
- **Visualization**: Generate performance charts and trade analysis

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`:
  - yfinance
  - pandas
  - matplotlib
  - numpy
  - scikit-learn
  - ta (Technical Analysis library)
  - requests
  - beautifulsoup4
  - html5lib

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mcapEXP.git
   cd mcapEXP
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script to perform a backtest:

```
python main.py
```

The default configuration tests an RSI and MACD-based strategy on Apple (AAPL) stock. You can modify the parameters in `main.py` to test different strategies, time periods, or stocks.

### Project Structure

- `main.py`: Entry point for running backtests
- `data_handler.py`: Handles data retrieval and preprocessing
- `strategy.py`: Implements trading strategies and signal generation
- `backtester.py`: Executes the backtest and calculates performance metrics
- `yahoo_api.py`: Interfaces with Yahoo Finance API for data retrieval

## Trading Strategies

The default strategy combines multiple technical indicators:

1. **RSI (Relative Strength Index)**: Generates buy signals when RSI is below the oversold threshold and sell signals when above the overbought threshold
2. **MACD Crossovers**: Generates signals when the MACD line crosses the signal line
3. **SMA (Simple Moving Average) Crossovers**: Generates signals when the short-term SMA crosses the long-term SMA

## Customization

You can create custom strategies by modifying the `TradingStrategy` class in `strategy.py` or by creating new strategy classes that follow the same interface.

## License

[MIT License](LICENSE)

## Disclaimer

This software is for educational and research purposes only. It is not intended to provide investment advice. Always do your own research and consult with a professional financial advisor before making investment decisions. 