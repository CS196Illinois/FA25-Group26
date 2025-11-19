"use client";

import { useState, useEffect } from 'react';
import { getPortfolioData } from '../../lib/api';
import './IndexPerformance.css';

export default function IndexPerformance() {
  const [indices, setIndices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const indexMapping = {
    'SPY': 'S&P 500',
    'QQQ': 'NASDAQ',
    'DIA': 'Dow Jones'
  };

  useEffect(() => {
    const fetchIndices = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch all indices in one request
        const data = await getPortfolioData(['SPY', 'QQQ', 'DIA']);
        
        // Transform the data
        const indexData = data.portfolio.map(stock => ({
          name: indexMapping[stock.ticker],
          ticker: stock.ticker,
          price: stock.currentPrice,
          change: ((stock.currentPrice - stock.previousClose) / stock.previousClose * 100),
          volume: stock.volume
        }));
        
        setIndices(indexData);
      } catch (err) {
        setError('Failed to fetch index data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchIndices();
  }, []);

  if (loading) {
    return (
      <div className="indexContainer">
        <h2 className="indexTitle">Index Performance</h2>
        <div className="loading">Loading indices...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="indexContainer">
        <h2 className="indexTitle">Index Performance</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="indexContainer">
      <h2 className="indexTitle">Index Performance</h2>
      <div className="indexTableWrapper">
        <table className="indexTable">
          <thead>
            <tr>
              <th>Index</th>
              <th>Price</th>
              <th>Change</th>
            </tr>
          </thead>
          <tbody>
            {indices.map((index) => (
              <tr key={index.ticker}>
                <td>{index.name}</td>
                <td>${index.price.toFixed(2)}</td>
                <td className={index.change >= 0 ? 'positive' : 'negative'}>
                  {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}