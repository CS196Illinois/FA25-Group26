import PortfolioPerformance from "../components/Blocks/PortfolioPerformance";
import NewsFeed from "../components/Blocks/NewsFeed";

export default function PortfolioTracker() {
    return (
        <div style={{ padding: '2rem'}}> 
            <h1 style={{ color: 'white' }}>Portfolio Tracker</h1>
            <PortfolioPerformance />
            <NewsFeed />
        </div>
    );
}