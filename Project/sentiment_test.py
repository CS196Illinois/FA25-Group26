import feedparser
import ssl
from transformers import pipeline

# Fix SSL certificate issue
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Initialize the sentiment analysis model (only once)
pipe = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")

# ---------------------------------------
# Fetch financial articles from multiple sources
# ---------------------------------------
def get_articles(ticker, keyword):
    rss_feeds = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        "https://www.marketwatch.com/rss/topstories",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.investing.com/rss/news.rss",
        "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
        f"https://news.google.com/rss/search?q={keyword}+stock&hl=en-US&gl=US&ceid=US:en",
    ]

    articles = []
    for url in rss_feeds:
        feed = feedparser.parse(url)
        if feed.bozo:
            print(f"⚠️  Could not parse feed {url}: {feed.bozo_exception}")
            continue

        for entry in feed.entries:
            text = (entry.title + " " + entry.get("summary", "")).lower()
            if keyword.lower() in text:
                articles.append({
                    "title": entry.title,
                    "summary": entry.get("summary", ""),
                    "link": entry.link,
                    "source": url.split("/")[2],
                })

    return articles


# ---------------------------------------
# Analyze sentiment of the collected articles
# ---------------------------------------
def analyze_sentiment(ticker: str, keyword: str):
    articles = get_articles(ticker, keyword)
    print(f"\n📈 Found {len(articles)} articles mentioning '{keyword}' across multiple sources.\n")

    total_score = 0
    num_article = 0

    for entry in articles:
        print(f"Source: {entry['source']}")
        print(f"Title: {entry['title']}")
        print(f"Link: {entry['link']}")
        print(f"Summary: {entry['summary']}\n")

        try:
            sentiment = pipe(entry["summary"] or entry["title"])[0]
            print(f"Sentiment: {sentiment['label']}, Score: {sentiment['score']:.4f}")
            print("=" * 60)

            if sentiment["label"] == "POS":
                total_score += sentiment["score"]
                num_article += 1
            elif sentiment["label"] == "NEG":
                total_score -= sentiment["score"]
                num_article += 1
        except Exception as e:
            print(f"Error processing article: {e}")
            continue

    if num_article > 0:
        final_score = total_score / num_article
        if final_score > 0.15:
            sentiment_label = "Positive"
        elif final_score < -0.15:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
    else:
        final_score = 0
        sentiment_label = "Neutral"

    print(f"\n🔎 Overall Sentiment for {ticker.upper()}: {sentiment_label} ({final_score:.4f})")
    print(f"📰 Articles analyzed: {num_article}")

    if sentiment_label == "Positive":
        recommendation = "✅ Consider investing in this company."
    elif sentiment_label == "Negative":
        recommendation = "⚠️  Consider avoiding investment for now."
    else:
        recommendation = "🕒 Hold or wait for more information before investing."

    print(f"💡 Recommendation: {recommendation}")


# ---------------------------------------
# Run from terminal
# ---------------------------------------
if __name__ == "__main__":
    ticker = input("Enter the stock ticker (e.g., TSLA): ").strip()
    keyword = input(f"Enter a keyword to search for (default: {ticker}): ").strip() or ticker
    analyze_sentiment(ticker, keyword)

