"use client";

import { useState, useEffect } from 'react';
import { getNewsSentiment } from '../../lib/api';
import styles from './NewsFeed.module.css';

const getSentimentClass = (sentiment) => {
  if (sentiment === "bullish") return styles.bullish;
  if (sentiment === "bearish") return styles.bearish;
  if (sentiment === "neutral") return styles.mixed;
  return '';
};

export default function NewsFeed({ ticker = 'AAPL' }) {
  const [newsData, setNewsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch news sentiment from Flask backend
        const data = await getNewsSentiment(ticker);
        
        // Transform the data to match our component structure
        const transformedNews = data.articles.map((article, index) => ({
          id: index,
          headline: article.title,
          sentiment: article.sentiment.charAt(0).toUpperCase() + article.sentiment.slice(1), // Capitalize first letter
          source: "Yahoo Finance", // You can parse this from the link if needed
          timestamp: formatTimestamp(article.published),
          link: article.link,
          confidence: article.confidence
        }));

        setNewsData(transformedNews);
      } catch (err) {
        setError('Failed to fetch news');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();

    // Optional: Refresh every 10 minutes
    const interval = setInterval(fetchNews, 600000);
    return () => clearInterval(interval);
  }, [ticker]);

  // Helper function to format timestamp
  const formatTimestamp = (published) => {
    try {
      const pubDate = new Date(published);
      const now = new Date();
      const diffMs = now - pubDate;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return "just now";
      if (diffMins < 60) return `${diffMins} min ago`;
      if (diffHours < 24) return `${diffHours} hrs ago`;
      if (diffDays === 1) return "yesterday";
      return `${diffDays} days ago`;
    } catch (e) {
      return published;
    }
  };

  if (loading) {
    return (
      <>
        <h2 className={styles.title}>News Feed</h2>
        <div className={styles.loading}>Loading news...</div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <h2 className={styles.title}>News Feed</h2>
        <div className={styles.error}>{error}</div>
      </>
    );
  }

  return (
    <>
      <h2 className={styles.title}>News Feed</h2>

      <div className={styles.newsList}>
        {newsData.map(item => (
          <article key={item.id} className={styles.newsItem}>
            <a 
              href={item.link} 
              target="_blank" 
              rel="noopener noreferrer" 
              className={styles.headlineLink}
            >
              <p className={styles.headline}>{item.headline}</p>
            </a>
            
            <span className={`${styles.sentiment} ${getSentimentClass(item.sentiment.toLowerCase())}`}>
              {item.sentiment}
            </span>
            
            <p className={styles.source}>
              {item.source} • {item.timestamp}
            </p>
          </article>
        ))}
      </div>
    </>
  );
}