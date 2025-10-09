#polling for crypto data every 30 seconds (no streaming support in free tier)
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, CryptoQuoteRequest, CryptoTradesRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import time

# No API keys needed for crypto historical data
client = CryptoHistoricalDataClient()

def get_recent_trades():
    """Get recent trades (polling instead of streaming)"""
    end = datetime.now()
    start = end - timedelta(minutes=10)  # Last 10 minutes
    
    request = CryptoTradesRequest(
        symbol_or_symbols=["BTC/USD", "ETH/USD"],
        start=start,
        end=end
    )
    
    trades = client.get_crypto_trades(request)
    return trades

def get_recent_bars():
    """Get recent price bars"""
    end = datetime.now()
    start = end - timedelta(hours=1)  # Last hour
    
    request = CryptoBarsRequest(
        symbol_or_symbols=["BTC/USD", "ETH/USD"],
        timeframe=TimeFrame.Minute,
        start=start,
        end=end
    )
    
    bars = client.get_crypto_bars(request)
    return bars

# Poll for data every 30 seconds
print("Polling for crypto data every 30 seconds...")
print("Press Ctrl+C to stop\n")

try:
    while True:
        print(f"\n=== {datetime.now().strftime('%H:%M:%S')} ===")
        
        # Get and display recent bars
        bars = get_recent_bars()
        if not bars.df.empty:
            latest_btc = bars.df.xs('BTC/USD', level='symbol').iloc[-1]
            latest_eth = bars.df.xs('ETH/USD', level='symbol').iloc[-1]
            print(f"BTC: ${latest_btc['close']:.2f}")
            print(f"ETH: ${latest_eth['close']:.2f}")
        else:
            print("No data received")
        
        time.sleep(30)  # Wait 30 seconds
        
except KeyboardInterrupt:
    print("\nStopped polling")

#Live data (haven't figured out how to display yet))
# from alpaca.data.live import StockDataStream


# wss_client = StockDataStream('api-key', 'secret-key')

# # async handler
# async def quote_data_handler(data):
#     # quote data will arrive here
#     print(data)

# wss_client.subscribe_quotes(quote_data_handler, "SPY")

# wss_client.run()