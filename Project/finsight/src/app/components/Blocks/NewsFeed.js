import styles from './NewsFeed.module.css';

const mockNewsData = [
  {
    id: 1,
    headline: "S&P 500 hits record high as inflation worries ease.",
    sentiment: "Bullish",
    source: "NBC",
    timestamp: "10 min ago"
  },
  {
    id: 2,
    headline: "Microsoft (MSFT) stock jumps after surprising Q3 earnings report.",
    sentiment: "Bullish",
    source: "Wall Street Journal",
    timestamp: "2 hrs ago"
  },
  {
    id: 3,
    headline: "TSLA drops after analyst downgrades valuation based on demand outlook.",
    sentiment: "Bearish",
    source: "Social Media Tracker",
    timestamp: "5 min ago"
  },
  {
    id: 4,
    headline: "Fed chair signals potential rate pause following latest CPI data release.",
    sentiment: "Mixed",
    source: "Reuters",
    timestamp: "45 sec ago"
  },
  {
    id: 5,
    headline: "example",
    sentiment: "Mixed",
    source: "Reuters",
    timestamp: "45 sec ago"
  }
];

const getSentimentClass = (sentiment) => {
  if (sentiment === "Bullish") return styles.bullish;
  if (sentiment === "Bearish") return styles.bearish;
  if (sentiment === "Mixed") return styles.mixed;
  return '';
};

export default function NewsFeed() {
    return (
      <>
        
        <h2 className ={styles.title} >News Feed</h2>
  
        <div className={styles.newsList}>
          
          {mockNewsData.map(item => (
            <article key={item.id} className={styles.newsItem}>
              
              <p className={styles.headline}>{item.headline}</p>
              
              <span className={`${styles.sentiment} ${getSentimentClass(item.sentiment)}`}>
                {item.sentiment}
              </span>
              
              <p className={styles.source}>
                {item.source} + {item.timestamp}
              </p>
              
            </article>
          ))}
        </div>
        
      </>
    );
  }