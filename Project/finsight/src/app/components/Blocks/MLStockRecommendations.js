"use client";

import React, { useState, useEffect } from "react";
import { getDetailedForecast } from '../../lib/api';
import "./MLStockRecommendations.css";

export default function MLStockRecommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // List of stocks to analyze
  const stocksToAnalyze = ["TSLA", "MSFT", "AAPL", "JPM", "NVDA", "BABA", "ADBE", "CAT"];

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch forecast data for all stocks in parallel
        const promises = stocksToAnalyze.map(ticker =>
          getDetailedForecast(ticker, 5, 10) // 5 day forecast
            .catch(err => {
              console.log(`Skipping ${ticker}: ${err.message}`);
              return null; // Return null for failed requests
            })
        );

        const results = await Promise.all(promises);

        // Transform the data, filtering out nulls (failed requests)
        const recs = results
          .map((result, idx) => {
            if (!result) return null; // Skip failed requests

            const decision = result.decision;
            const predictedReturn = decision.pred_return_h;
            const buySignal = decision.buy;

            // Determine action based on ML model signals
            let action;
            if (buySignal && predictedReturn > 0.02) {
              action = "Buy";
            } else if (predictedReturn < -0.02) {
              action = "Sell";
            } else {
              action = "Hold";
            }

            return {
              symbol: stocksToAnalyze[idx],
              change: `${predictedReturn >= 0 ? '+' : ''}${(predictedReturn * 100).toFixed(1)}%`,
              action: action,
              predictedReturn: predictedReturn
            };
          })
          .filter(rec => rec !== null); // Remove nulls

        // Sort by predicted return (best opportunities first)
        recs.sort((a, b) => b.predictedReturn - a.predictedReturn);

        setRecommendations(recs);
      } catch (err) {
        setError("Failed to fetch recommendations");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();

    // Optional: Refresh every 5 minutes
    const interval = setInterval(fetchRecommendations, 300000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="mlContainer">
        <h2 className="mlTitle">ML Stock Recommendations</h2>
        <div className="loading">Analyzing stocks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mlContainer">
        <h2 className="mlTitle">ML Stock Recommendations</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="mlContainer">
      <h2 className="mlTitle">ML Stock Recommendations</h2>

      <div className="tableWrapper">
        <table className="mlTable">
          <thead>
            <tr>
              <th>Stock</th>
              <th>Change</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec, index) => (
              <tr key={index}>
                <td>{rec.symbol}</td>
                <td
                  className={
                    rec.change.startsWith("+") ? "positive" : "negative"
                  }
                >
                  {rec.change}
                </td>
                <td>{rec.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}