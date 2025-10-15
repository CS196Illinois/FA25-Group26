import feedparser
import ssl
from transformers import pipeline

# Fix SSL certificate issue
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Initialize the sentiment analysis pipeline
pipe = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")

# Feeding the model with articles to get sentiment
ticker = 'META'
keyword = 'meta'
rss_url = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US'
feed = feedparser.parse(rss_url)

# Check if feed was parsed successfully
if feed.bozo:
    print(f"Warning: There was an issue parsing the feed: {feed.bozo_exception}")

total_score = 0
num_article = 0

print(f"Found {len(feed.entries)} articles in feed")

for i, entry in enumerate(feed.entries):
    if keyword.lower() not in entry.summary.lower():
        continue
    
    print(f'Title: {entry.title}')
    print(f'Link: {entry.link}')
    print(f'Published: {entry.published}')
    print(f'Summary: {entry.summary}')

    try:
        sentiment = pipe(entry.summary)[0]
        print(f'Sentiment: {sentiment["label"]}, Score: {sentiment["score"]:.4f}')
        print("=" * 40)

        if sentiment["label"] == 'POS':  # Positive
            total_score += sentiment['score']
            num_article += 1
        elif sentiment["label"] == 'NEG':  # Negative
            total_score -= sentiment['score']
            num_article += 1
        # Neutral sentiments are ignored in scoring
    except Exception as e:
        print(f"Error processing article: {e}")
        continue

if num_article > 0:
    final_score = total_score / num_article
    # Fixed the logical error here - was comparing > 0.15 for both positive and negative
    if final_score > 0.15:
        sentiment_label = "Positive"
    elif final_score < -0.15:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
else:
    final_score = 0
    sentiment_label = "Neutral"

print(f'Overall sentiment: {sentiment_label} ({final_score:.4f})')
print(f'Articles analyzed: {num_article}')