import MLStockRecommendations from '../components/Blocks/MLStockRecommendations';
import SentimentSignals from '../components/Blocks/SentimentSignals';
import IndexPerformance from '../components/Blocks/IndexPerformance';

export default function ModelInsights() {
    return (
        <div style={{ padding: '2rem' }}>
            <h1 style={{ color: 'white' }}>Model Insights</h1>
            <MLStockRecommendations />
            <SentimentSignals />
            <IndexPerformance />
        </div>
    );
}