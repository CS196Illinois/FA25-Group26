

export default function Home() {
  return (
    <div className={styles.content}>
        <div className={styles.block}>
          <h2>ML Stock Recommendations</h2>
          <p>Predicted buy/sell opportunities based on ML models.</p>
        </div>
        <div className={styles.block}>
          <h2>Index Performance</h2>
          <p>Performance overview for S&P 500, Nasdaq, and Dow Jones.</p>
        </div>
        <div className={styles.block}>
          <h2>Portfolio Performance</h2>
          <p>Your portfolio's gains/losses and historical trend charts.</p>
        </div>
        <div className={styles.block}>
          <h2>Sentiment Signals</h2>
          <p>Market sentiment analysis based on social and news data.</p>
        </div>
        <div className={styles.block}>
          <h2>News Feed</h2>
          <p>Latest stock market and company news updates.</p>
        </div>
      </div>

  )
}