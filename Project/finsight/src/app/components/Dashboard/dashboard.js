import styles from './Dashboard.module.css';
import MLStockRecommendations from '../Blocks/MLStockRecommendations';
import IndexPerformance from '../Blocks/IndexPerformance';
import PortfolioPerformance from '../Blocks/PortfolioPerformance';
import SentimentSignals from '../Blocks/SentimentSignals';
import NewsFeed from '../Blocks/NewsFeed';

export default function Dashboard() {
  return (


    <div className={styles.content}>
        <div className={styles.block}>
          <MLStockRecommendations />
        </div>
        <div className={styles.block}>
          <IndexPerformance />
        </div>
        <div className={styles.block}>
          <PortfolioPerformance />
        </div>
        <div className={styles.block}>
          <SentimentSignals />
        </div>
        <div className={styles.block}>
          <NewsFeed />
        </div>
      </div>

  )
}