import yfinance as yf
import pandas as pd
from datetime import datetime

# ---------------------------------------
# Mock portfolio (replace later with real user data)
# ---------------------------------------
portfolio = [
    {"ticker": "AAPL", "company": "Apple Inc.", "shares": 25},
    {"ticker": "TSLA", "company": "Tesla Inc.", "shares": 10},
    {"ticker": "MSFT", "company": "Microsoft Corp.", "shares": 15},
    {"ticker": "NVDA", "company": "NVIDIA Corp.", "shares": 8},
    {"ticker": "AMZN", "company": "Amazon.com Inc.", "shares": 12},
]

# ---------------------------------------
# Fetch live market data using yfinance
# ---------------------------------------
def fetch_market_data(portfolio):
    tickers = [p["ticker"] for p in portfolio]
    data = yf.download(tickers, period="1d", interval="1m", progress=False)

    # Get the most recent price for each ticker
    latest_prices = {}
    for ticker in tickers:
        try:
            latest_prices[ticker] = data["Close"][ticker].dropna().iloc[-1]
        except Exception:
            latest_prices[ticker] = None
    return latest_prices


# ---------------------------------------
# Display the portfolio with live trends
# ---------------------------------------
def display_portfolio(portfolio):
    print(f"\n📊 Portfolio Overview ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("=" * 70)

    prices = fetch_market_data(portfolio)
    total_value = 0

    print(f"{'Company':<20}{'Ticker':<8}{'Shares':<8}{'Price ($)':<12}{'Value ($)':<12}")
    print("-" * 70)

    for p in portfolio:
        ticker = p["ticker"]
        price = prices.get(ticker)
        if price:
            value = price * p["shares"]
            total_value += value
            print(f"{p['company']:<20}{ticker:<8}{p['shares']:<8}{price:<12.2f}{value:<12.2f}")
        else:
            print(f"{p['company']:<20}{ticker:<8}{p['shares']:<8}{'N/A':<12}{'N/A':<12}")

    print("-" * 70)
    print(f"{'Total Portfolio Value:':<50}${total_value:,.2f}")
    print("=" * 70)


# ---------------------------------------
# Run script
# ---------------------------------------
if __name__ == "__main__":
    display_portfolio(portfolio)
