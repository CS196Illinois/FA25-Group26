from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

# no keys required for crypto data
client = CryptoHistoricalDataClient()

request_params = CryptoBarsRequest(
    symbol_or_symbols=["BTC/USD", "ETH/USD"],
    timeframe=TimeFrame.Day,
    start=datetime(2022, 7, 1),
    end=datetime(2022, 9, 1)
)

bars = client.get_crypto_bars(request_params)

# Convert to dataframe and print it
print("=== Crypto Bars Data ===")
print(bars.df)

# Print some basic info
print(f"\n=== Data Summary ===")
print(f"Number of records: {len(bars.df)}")
print(f"Date range: {bars.df.index.get_level_values('timestamp').min()} to {bars.df.index.get_level_values('timestamp').max()}")

# Access specific symbol data - FIXED: Use list indexing instead of .head()
print(f"\n=== BTC/USD Sample (first 5 records) ===")
btc_data = bars["BTC/USD"]
for i in range(min(5, len(btc_data))):  # Show first 5 or fewer if list is shorter
    print(btc_data[i])

print(f"\n=== ETH/USD Sample (first 5 records) ===")
eth_data = bars["ETH/USD"]
for i in range(min(5, len(eth_data))):  # Show first 5 or fewer if list is shorter
    print(eth_data[i])

# Alternative: Convert the list to DataFrame for easier viewing
import pandas as pd
print(f"\n=== BTC/USD as DataFrame ===")
btc_df = pd.DataFrame([bar.__dict__ for bar in btc_data])
print(btc_df.head())