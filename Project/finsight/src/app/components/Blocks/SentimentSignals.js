'use client';

import { useEffect, useState } from 'react';
import { getNewsSentiment } from '../../lib/api';
import styles from './Sentiment.module.css'; 

export default function SentimentSignals() {
    const [sentimentData, setSentimentData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Stocks to track sentiment for
    const stocksToTrack = ['TSLA', 'NFLX', 'GOOG', 'AMZN', 'AAPL', 'MSFT'];

    useEffect(() => {
        const fetchSentimentData = async () => {
            setLoading(true);
            setError(null);

            try {
                // Fetch sentiment for all stocks in parallel
                const promises = stocksToTrack.map(ticker => 
                    getNewsSentiment(ticker)
                );

                const results = await Promise.all(promises);

                // Transform the data
                const transformedData = results.map((result, idx) => {
                    // Get the most recent article with non-neutral sentiment
                    const significantArticle = result.articles.find(
                        article => article.sentiment !== 'neutral'
                    ) || result.articles[0];

                    // Map sentiment to +/-
                    const sentimentSymbol = result.overallSentiment === 'bullish' ? '+' : 
                                           result.overallSentiment === 'bearish' ? '-' : '~';

                    return {
                        stock: stocksToTrack[idx],
                        sentiment: sentimentSymbol,
                        source: 'Yahoo Finance',
                        timestamp: formatTimestamp(significantArticle?.published),
                        confidence: significantArticle?.confidence || 0,
                        overallSentiment: result.overallSentiment
                    };
                });

                // Sort by most recent first
                transformedData.sort((a, b) => {
                    const timeA = parseTimestamp(a.timestamp);
                    const timeB = parseTimestamp(b.timestamp);
                    return timeA - timeB;
                });

                setSentimentData(transformedData);
            } catch (err) {
                setError('Failed to fetch sentiment data');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchSentimentData();

        // Optional: Refresh every 10 minutes
        const interval = setInterval(fetchSentimentData, 600000);
        return () => clearInterval(interval);
    }, []);

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
            if (diffMins < 60) return `${diffMins} min`;
            if (diffHours < 24) return `${diffHours} hours`;
            if (diffDays === 1) return "1 day";
            return `${diffDays} days`;
        } catch (e) {
            return "N/A";
        }
    };

    // Helper to parse timestamp for sorting
    const parseTimestamp = (timestamp) => {
        if (!timestamp || timestamp === "N/A") return Infinity;
        
        const parts = timestamp.split(' ');
        const value = parseInt(parts[0]);
        const unit = parts[1];

        if (unit.startsWith('min')) return value;
        if (unit.startsWith('hour')) return value * 60;
        if (unit.startsWith('day')) return value * 1440;
        return 0;
    };

    if (loading) {
        return (
            <div className={styles.sentimentContainer}>
                <h2 className={styles.title}>Sentiment Signals</h2>
                <div className={styles.loading}>Analyzing sentiment...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.sentimentContainer}>
                <h2 className={styles.title}>Sentiment Signals</h2>
                <div className={styles.error}>{error}</div>
            </div>
        );
    }

    return (
        <div className={styles.sentimentContainer}>
            <h2 className={styles.title}>Sentiment Signals</h2>
            
            <div className={styles.tableWrapper}>
                <table className={styles.sentimentTable}>
                    <thead>
                        <tr>
                            <th>Stock</th>
                            <th>Sentiment</th>
                            <th>Source</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sentimentData.map((signal, index) => (
                            <tr key={index}>
                                <td>{signal.stock}</td>
                                <td className={signal.sentiment === '+' ? styles.positive : 
                                              signal.sentiment === '-' ? styles.negative : 
                                              styles.neutral}>
                                    {signal.sentiment}
                                </td>
                                <td>{signal.source}</td>
                                <td>{signal.timestamp}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}