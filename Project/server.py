# ============================================================================
# IMPORTS
# ============================================================================

# Flask is the web framework used to create the API server
from flask import Flask, request, jsonify
# CORS (Cross-Origin Resource Sharing) allows frontend apps from different domains to make requests
from flask_cors import CORS

# yfinance is used to fetch real-time stock market data from Yahoo Finance
import yfinance as yf

# feedparser is used to parse RSS feeds for financial news
import feedparser

# ssl module handles secure connections for RSS feed fetching
import ssl

# Transformers library provides pre-trained NLP models for sentiment analysis
from transformers import pipeline

# datetime utilities for timestamps and time-based calculations
from datetime import datetime, timedelta

# Import the forecast model for advanced stock predictions
from forecast_model_final import run_forecast

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

# Create the Flask application instance
app = Flask(__name__)

# Enable CORS to allow requests from frontend applications running on different ports/domains
# This is essential for React/Vue/Angular apps that typically run on localhost:3000
# while the Flask server runs on localhost:5000
CORS(app)

# ============================================================================
# SSL CONFIGURATION
# ============================================================================

# Fix SSL certificate verification issues when fetching RSS feeds
# Some RSS feeds may have certificate issues, this creates an unverified context as a workaround
# Note: In production, you should properly verify SSL certificates for security
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# ============================================================================
# SENTIMENT ANALYSIS MODEL SETUP
# ============================================================================

# Global variable to store the sentiment analysis pipeline
# Initially set to None to enable lazy loading (load only when needed)
sentiment_pipeline = None

def get_sentiment_pipeline():
    """
    Lazy load the sentiment analysis model to avoid startup delays.

    The sentiment model is large and takes time to load into memory.
    By lazy loading, we only load it when the first sentiment analysis request comes in,
    rather than at server startup. This makes the server start faster.

    Returns:
        pipeline: Transformers sentiment analysis pipeline using BERTweet model
                  This model is specifically trained for social media text and works well for financial news
    """
    global sentiment_pipeline

    # Check if the model has already been loaded
    if sentiment_pipeline is None:
        # Load the BERTweet sentiment analysis model
        # This model can classify text as positive (POS), negative (NEG), or neutral (NEU)
        sentiment_pipeline = pipeline("sentiment-analysis",
                                     model="finiteautomata/bertweet-base-sentiment-analysis")
    return sentiment_pipeline

# ============================================================================
# API ENDPOINT: STOCK DATA AND PREDICTION
# ============================================================================

@app.route('/api/stock/predict', methods=['POST'])
def get_stock_data():
    """
    API endpoint to get current stock data and basic trend prediction.

    This endpoint fetches real-time stock data from Yahoo Finance and performs
    a simple trend analysis based on the 5-day moving average.

    Request Format (JSON):
        POST /api/stock/predict
        {
            "ticker": "AAPL"  // Stock ticker symbol (e.g., AAPL for Apple)
        }

    Response Format (JSON):
        {
            "ticker": "AAPL",
            "company": "Apple Inc.",
            "currentPrice": 175.50,
            "previousClose": 174.20,
            "priceChange": 1.30,
            "priceChangePercent": 0.75,
            "volume": 50000000,
            "trend": "bullish",  // or "bearish"
            "fiftyTwoWeekHigh": 199.62,
            "fiftyTwoWeekLow": 124.17,
            "marketCap": 2800000000000,
            "timestamp": "2024-11-12T10:30:00"
        }
    """
    try:
        # ===== STEP 1: EXTRACT AND VALIDATE INPUT =====
        # Get the JSON data from the request body
        data = request.get_json()

        # Extract the ticker symbol and convert to uppercase (stock tickers are always uppercase)
        ticker = data.get('ticker', '').upper()

        # Validate that a ticker was provided
        if not ticker:
            # Return 400 Bad Request if no ticker is provided
            return jsonify({'error': 'Ticker symbol is required'}), 400

        # ===== STEP 2: FETCH STOCK DATA =====
        # Create a yfinance Ticker object for the requested stock
        # This object provides access to all stock data and methods
        stock = yf.Ticker(ticker)

        # Get general information about the stock (company name, market cap, etc.)
        # info is a dictionary containing metadata about the stock
        info = stock.info

        # Fetch historical price data for the last 5 days
        # This returns a DataFrame with columns: Open, High, Low, Close, Volume
        # We use 5 days to calculate the moving average for trend prediction
        hist = stock.history(period='5d')

        # Check if we successfully got data
        if hist.empty:
            # Return 404 Not Found if no data is available (invalid ticker or data not available)
            return jsonify({'error': 'Unable to fetch stock data'}), 404

        # ===== STEP 3: CALCULATE METRICS =====
        # Get the most recent closing price (last row in the DataFrame)
        # iloc[-1] gets the last row
        current_price = hist['Close'].iloc[-1]

        # Get yesterday's closing price for comparison
        # Try to get it from info first, fallback to second-to-last historical price
        previous_close = info.get('previousClose', hist['Close'].iloc[-2])

        # Calculate the dollar change from previous close
        price_change = current_price - previous_close

        # Calculate the percentage change
        # Formula: (change / previous) * 100
        price_change_percent = (price_change / previous_close) * 100

        # ===== STEP 4: PERFORM TREND PREDICTION =====
        # Use the advanced forecast model to predict future prices and generate trading signals
        try:
            # Run the forecast model with default parameters
            # This will analyze historical data and generate predictions
            forecast_result = run_forecast(
                ticker=ticker,
                parquet_path='stock_data_since_2016.parquet',
                lags=10,          # Use 10 previous days for prediction
                horizon=5,        # Predict 5 days ahead for quick trend assessment
                per_rows=5000     # Use last 5000 rows of historical data
            )

            # Extract decision metrics from the forecast
            decision = forecast_result['decision']

            # Determine trend based on forecast model's buy signal and predicted return
            # If buy signal is True and predicted return is positive, trend is bullish
            if decision['buy'] and decision['pred_return_h'] > 0:
                trend = 'bullish'
            # If predicted return is significantly negative, trend is bearish
            elif decision['pred_return_h'] < -0.02:  # More than 2% predicted decline
                trend = 'bearish'
            else:
                trend = 'neutral'

            # Add forecast-specific data
            predicted_price = forecast_result['pred_last']
            signal_strength = decision['signal_to_noise']

        except Exception as forecast_error:
            # If forecast model fails, fall back to simple moving average
            print(f"Forecast model error: {forecast_error}")
            avg_5d = hist['Close'].mean()
            trend = 'bullish' if current_price > avg_5d else 'bearish'
            predicted_price = None
            signal_strength = None

        # ===== STEP 5: BUILD RESPONSE =====
        # Create a dictionary with all the calculated data
        response = {
            'ticker': ticker,  # Stock symbol
            'company': info.get('longName', ticker),  # Full company name, fallback to ticker if not available
            'currentPrice': round(current_price, 2),  # Round to 2 decimal places for currency
            'previousClose': round(previous_close, 2),
            'priceChange': round(price_change, 2),
            'priceChangePercent': round(price_change_percent, 2),
            'volume': int(hist['Volume'].iloc[-1]),  # Number of shares traded today
            'trend': trend,  # Our calculated trend (bullish/bearish/neutral)
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),  # Highest price in last 52 weeks
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow'),  # Lowest price in last 52 weeks
            'marketCap': info.get('marketCap'),  # Total market value of the company
            'timestamp': datetime.now().isoformat()  # When this data was generated
        }

        # Add forecast-specific fields if available
        if predicted_price is not None:
            response['predictedPrice'] = round(predicted_price, 2)
            response['predictedChange'] = round(predicted_price - current_price, 2)
            response['predictedChangePercent'] = round(((predicted_price - current_price) / current_price) * 100, 2)

        if signal_strength is not None:
            response['signalStrength'] = round(signal_strength, 2)

        # Return the response as JSON with 200 OK status
        return jsonify(response)

    except Exception as e:
        # ===== ERROR HANDLING =====
        # If anything goes wrong (network error, invalid ticker, etc.)
        # Return a 500 Internal Server Error with the error message
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINT: DETAILED STOCK FORECAST
# ============================================================================

@app.route('/api/stock/forecast', methods=['POST'])
def get_detailed_forecast():
    """
    API endpoint to get detailed stock forecast with trading signals.

    This endpoint uses the advanced forecast model to generate multi-day predictions,
    risk metrics, and trading recommendations based on historical data analysis.

    Request Format (JSON):
        POST /api/stock/forecast
        {
            "ticker": "AAPL",       // Required: Stock ticker symbol
            "horizon": 20,          // Optional: Number of days to forecast (default: 20)
            "lags": 10              // Optional: Number of historical days to use (default: 10)
        }

    Response Format (JSON):
        {
            "ticker": "AAPL",
            "lastClose": 175.50,
            "predictedLast": 178.30,
            "horizon": 20,
            "lags": 10,
            "forecast": [
                {
                    "date": "2024-11-13",
                    "ticker": "AAPL",
                    "pred_close": 176.20
                },
                ...
            ],
            "decision": {
                "pred_return_h": 0.0159,
                "uncert_h": 0.0234,
                "signal_to_noise": 0.68,
                "slope_pred": 0.14,
                "max_drawdown_pred": 0.012,
                "buy": true,
                "suggested_position_0to1": 0.68,
                "stop_loss_rel": -0.0234,
                "take_profit_rel": 0.0468
            },
            "timestamp": "2024-11-12T10:30:00"
        }
    """
    try:
        # ===== STEP 1: EXTRACT AND VALIDATE INPUT =====
        data = request.get_json()

        ticker = data.get('ticker', '').upper()
        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400

        # Optional parameters with defaults
        horizon = data.get('horizon', 20)
        lags = data.get('lags', 10)

        # ===== STEP 2: RUN FORECAST MODEL =====
        # Run the advanced forecast model
        try:
            forecast_result = run_forecast(
                ticker=ticker,
                parquet_path='stock_data_since_2016.parquet',
                lags=lags,
                horizon=horizon,
                per_rows=5000
            )
        except Exception as forecast_error:
            # If forecast fails, return error with 404
            print(f"Forecast error for {ticker}: {forecast_error}")
            return jsonify({'error': f'No data available for ticker {ticker}'}), 404

        # ===== STEP 3: BUILD RESPONSE =====
        # Add timestamp to the response
        forecast_result['timestamp'] = datetime.now().isoformat()

        # Rename keys to match camelCase convention for frontend
        response = {
            'ticker': forecast_result['ticker'],
            'lastClose': forecast_result['last_close'],
            'predictedLast': forecast_result['pred_last'],
            'horizon': forecast_result['horizon'],
            'lags': forecast_result['lags'],
            'forecast': forecast_result['forecast'],
            'decision': forecast_result['decision'],
            'timestamp': forecast_result['timestamp']
        }

        return jsonify(response)

    except ValueError as ve:
        # Handle specific forecast model errors (e.g., ticker not found)
        return jsonify({'error': str(ve)}), 404

    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error in forecast endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINT: NEWS SENTIMENT ANALYSIS
# ============================================================================

@app.route('/api/news/sentiment', methods=['POST'])
def get_news_sentiment():
    """
    API endpoint to analyze news sentiment for a given stock.

    This endpoint fetches recent financial news articles from Yahoo Finance RSS feed,
    analyzes each article's sentiment using a pre-trained NLP model, and returns
    both individual article sentiments and an overall sentiment score.

    Request Format (JSON):
        POST /api/news/sentiment
        {
            "ticker": "AAPL",      // Required: Stock ticker symbol
            "keyword": "apple"     // Optional: Filter articles by keyword
        }

    Response Format (JSON):
        {
            "ticker": "AAPL",
            "overallSentiment": "bullish",  // or "bearish" or "neutral"
            "sentimentScore": 0.45,
            "articlesAnalyzed": 8,
            "recommendation": "Consider investing in this company.",
            "articles": [
                {
                    "title": "Apple Reports Strong Q4 Earnings",
                    "link": "https://...",
                    "published": "Tue, 12 Nov 2024 10:30:00",
                    "summary": "Apple Inc. reported...",
                    "sentiment": "bullish",
                    "confidence": 0.89
                },
                ...
            ],
            "timestamp": "2024-11-12T10:30:00"
        }
    """
    try:
        # ===== STEP 1: EXTRACT AND VALIDATE INPUT =====
        # Get the JSON data from the request body
        data = request.get_json()

        # Extract ticker symbol (required) and convert to uppercase
        ticker = data.get('ticker', '').upper()

        # Extract keyword for filtering articles (optional)
        # If no keyword provided, use the ticker symbol as the keyword
        keyword = data.get('keyword', ticker).lower()

        # Validate that a ticker was provided
        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400

        # ===== STEP 2: LOAD SENTIMENT MODEL =====
        # Get the sentiment analysis pipeline (will lazy load if not already loaded)
        pipe = get_sentiment_pipeline()

        # ===== STEP 3: FETCH NEWS FEED =====
        # Construct the Yahoo Finance RSS feed URL for this ticker
        # This feed contains recent news articles about the stock
        rss_url = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US'

        # Parse the RSS feed
        # feedparser will fetch the XML and convert it to a Python dictionary
        feed = feedparser.parse(rss_url)

        # Check if there was an error parsing the feed
        # feed.bozo is True if there was a parsing error
        if feed.bozo:
            return jsonify({'error': 'Unable to fetch news feed'}), 500

        # ===== STEP 4: ANALYZE EACH ARTICLE =====
        # Initialize lists and counters for processing articles
        articles = []  # Will store article data with sentiment
        total_score = 0  # Running sum of sentiment scores
        num_articles = 0  # Count of articles analyzed (excluding neutral)

        # Process the first 10 articles from the feed
        # We limit to 10 to avoid processing too many articles and slowing down the response
        for entry in feed.entries[:10]:
            # Filter articles by keyword if provided
            # Skip articles that don't mention the keyword in their summary
            summary_text = entry.get('summary', entry.title)
            if keyword and keyword.lower() not in summary_text.lower():
                continue

            try:
                # Run the sentiment analysis model on the article summary
                # Returns: [{'label': 'POS'/'NEG'/'NEU', 'score': 0.0-1.0}]
                # Use title if summary is empty or too short
                text_to_analyze = summary_text if len(summary_text) > 20 else entry.title

                # Truncate text to avoid model errors (max 512 tokens)
                if len(text_to_analyze) > 500:
                    text_to_analyze = text_to_analyze[:500]

                sentiment = pipe(text_to_analyze)[0]

                # ===== MAP MODEL OUTPUT TO BULLISH/BEARISH =====
                # The model returns 'POS', 'NEG', or 'NEU' labels
                # We map these to financial terms: bullish, bearish, neutral

                if sentiment["label"] == 'POS':  # Positive sentiment
                    sentiment_label = 'bullish'
                    score = sentiment['score']  # Confidence score (0-1)
                    total_score += score  # Add to total (positive contribution)

                elif sentiment["label"] == 'NEG':  # Negative sentiment
                    sentiment_label = 'bearish'
                    score = sentiment['score']
                    total_score -= score  # Subtract from total (negative contribution)

                else:  # Neutral sentiment (NEU)
                    sentiment_label = 'neutral'
                    score = 0  # Neutral doesn't affect the score

                # Only count positive and negative articles in our total
                # Neutral articles are included in results but don't affect the overall score
                num_articles += 1 if sentiment["label"] in ['POS', 'NEG'] else 0

                # ===== BUILD ARTICLE OBJECT =====
                # Create a dictionary with article information and sentiment
                articles.append({
                    'title': entry.title,  # Article headline
                    'link': entry.link,  # URL to full article
                    'published': entry.get('published', 'Unknown'),  # Publication date/time
                    # Truncate summary to 200 characters to keep response size manageable
                    'summary': summary_text[:200] + '...' if len(summary_text) > 200 else summary_text,
                    'sentiment': sentiment_label,  # bullish/bearish/neutral
                    'confidence': round(sentiment['score'], 3)  # Model's confidence (0-1)
                })

            except Exception as e:
                # If there's an error processing this article, log it and continue
                # This ensures one bad article doesn't break the entire request
                print(f"Error processing article: {e}")
                import traceback
                traceback.print_exc()
                continue

        # ===== STEP 5: CALCULATE OVERALL SENTIMENT =====
        # Average the sentiment scores across all analyzed articles
        if num_articles > 0:
            # Calculate the average sentiment score
            # Positive scores indicate bullish sentiment, negative scores indicate bearish
            final_score = total_score / num_articles

            # Classify overall sentiment based on score thresholds
            # Score > 0.15: Strong positive sentiment = bullish
            if final_score > 0.15:
                overall_sentiment = "bullish"
                recommendation = "Consider investing in this company."

            # Score < -0.15: Strong negative sentiment = bearish
            elif final_score < -0.15:
                overall_sentiment = "bearish"
                recommendation = "Consider avoiding investment in this company for now."

            # Score between -0.15 and 0.15: Mixed or weak sentiment = neutral
            else:
                overall_sentiment = "neutral"
                recommendation = "Hold or wait for more information before investing."
        else:
            # No articles were analyzed (all were neutral or filtered out)
            final_score = 0
            overall_sentiment = "neutral"
            recommendation = "Insufficient data to make a recommendation."

        # ===== STEP 6: BUILD RESPONSE =====
        # Create the final response object with all data
        response = {
            'ticker': ticker,  # Stock symbol
            'overallSentiment': overall_sentiment,  # bullish/bearish/neutral
            'sentimentScore': round(final_score, 3),  # Average score
            'articlesAnalyzed': num_articles,  # Number of articles analyzed
            'recommendation': recommendation,  # Investment recommendation text
            'articles': articles,  # Array of individual article sentiments
            'timestamp': datetime.now().isoformat()  # When this analysis was performed
        }

        # Return the response as JSON
        return jsonify(response)

    except Exception as e:
        # ===== ERROR HANDLING =====
        # Catch any unexpected errors and return a 500 error
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINT: PORTFOLIO DATA
# ============================================================================

@app.route('/api/portfolio', methods=['POST'])
def get_portfolio_data():
    """
    API endpoint to get current data for multiple stocks in a portfolio.

    This endpoint allows you to fetch data for multiple stocks in a single request,
    which is more efficient than making individual requests for each stock.
    Useful for displaying a portfolio overview or watchlist.

    Request Format (JSON):
        POST /api/portfolio
        {
            "tickers": ["AAPL", "MSFT", "TSLA", "NVDA"]  // Array of stock ticker symbols
        }

    Response Format (JSON):
        {
            "portfolio": [
                {
                    "ticker": "AAPL",
                    "company": "Apple Inc.",
                    "currentPrice": 175.50,
                    "previousClose": 174.20,
                    "priceChange": 1.30,
                    "volume": 50000000
                },
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corporation",
                    "currentPrice": 380.25,
                    "previousClose": 378.90,
                    "priceChange": 1.35,
                    "volume": 25000000
                },
                ...
            ],
            "timestamp": "2024-11-12T10:30:00"
        }
    """
    try:
        # ===== STEP 1: EXTRACT AND VALIDATE INPUT =====
        # Get the JSON data from the request body
        data = request.get_json()

        # Extract the array of ticker symbols
        tickers = data.get('tickers', [])

        # Validate input
        # - Ensure tickers is provided
        # - Ensure tickers is actually a list (array)
        if not tickers or not isinstance(tickers, list):
            return jsonify({'error': 'Tickers array is required'}), 400

        # ===== STEP 2: FETCH DATA FOR EACH STOCK =====
        # Initialize list to store portfolio data
        portfolio_data = []

        # Loop through each ticker symbol in the list
        for ticker in tickers:
            try:
                # Create yfinance Ticker object for this stock
                stock = yf.Ticker(ticker.upper())

                # Get stock information (company name, previous close, etc.)
                info = stock.info

                # Get today's price data
                # We only need 1 day of history to get current price
                hist = stock.history(period='1d')

                # Check if we got valid data
                if not hist.empty:
                    # Extract current price (most recent closing price)
                    current_price = hist['Close'].iloc[-1]

                    # Build stock data object
                    portfolio_data.append({
                        'ticker': ticker.upper(),  # Stock symbol
                        'company': info.get('longName', ticker),  # Full company name
                        'currentPrice': round(current_price, 2),  # Current price
                        'previousClose': info.get('previousClose', 0),  # Yesterday's close
                        # Calculate price change from previous close
                        'priceChange': round(current_price - info.get('previousClose', 0), 2),
                        'volume': int(hist['Volume'].iloc[-1])  # Trading volume today
                    })

            except Exception as e:
                # If there's an error fetching data for this ticker, log it and continue
                # This ensures one bad ticker doesn't break the entire portfolio request
                print(f"Error fetching data for {ticker}: {e}")
                continue

        # ===== STEP 3: BUILD AND RETURN RESPONSE =====
        # Return the array of stock data with timestamp
        return jsonify({
            'portfolio': portfolio_data,  # Array of stock data objects
            'timestamp': datetime.now().isoformat()  # When this data was fetched
        })

    except Exception as e:
        # ===== ERROR HANDLING =====
        # Catch any unexpected errors
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINT: HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint to verify the server is running.

    This endpoint is useful for:
    - Monitoring tools to check if the server is alive
    - Frontend to verify backend connectivity before making actual requests
    - Load balancers to check server health

    Request Format:
        GET /api/health

    Response Format (JSON):
        {
            "status": "healthy",
            "timestamp": "2024-11-12T10:30:00"
        }
    """
    return jsonify({
        'status': 'healthy',  # Server status indicator
        'timestamp': datetime.now().isoformat()  # Current server time
    })

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == '__main__':
    """
    Start the Flask development server.

    Configuration:
    - debug=True: Enables debug mode which provides detailed error messages
                  and auto-reloads the server when code changes
                  WARNING: Never use debug=True in production!
    - port=5001: The server will listen on http://localhost:5001

    To run this server:
        python server.py

    The server will start and you can make requests to:
        http://localhost:5001/api/stock/predict
        http://localhost:5001/api/news/sentiment
        http://localhost:5001/api/portfolio
        http://localhost:5001/api/health
    """
    app.run(debug=True, port=5001)