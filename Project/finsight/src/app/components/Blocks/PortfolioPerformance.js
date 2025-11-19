"use client";

import { useState, useEffect } from "react";
import { getDetailedForecast } from '../../lib/api';
import "./PortfolioPerformance.css";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function PortfolioPerformance({ ticker = "SPY" }) {
  const [chartData, setChartData] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [horizon, setHorizon] = useState(5);

  useEffect(() => {
    const fetchPortfolioData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch forecast data
        const forecast = await getDetailedForecast(ticker, horizon, 10);

        // Transform forecast data for the chart
        const transformedData = forecast.forecast.map((item, index) => {
          // Format date to show day of week
          const date = new Date(item.date);
          const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
          const dayName = dayNames[date.getDay()];
          
          return {
            date: dayName,
            value: item.pred_close,
            fullDate: item.date
          };
        });

        setChartData(transformedData);

        // Calculate metrics from forecast decision
        const decision = forecast.decision;
        const predictedReturn = decision.pred_return_h;
        const uncertainty = decision.uncert_h;
        const signalToNoise = decision.signal_to_noise;

        // Calculate volatility (using uncertainty as a proxy)
        const volatility = uncertainty * 100;

        // Calculate today's return (difference between last predicted and current)
        const todayReturn = predictedReturn;

        setMetrics({
          todayReturn: (todayReturn * 100).toFixed(2),
          sharpeRatio: signalToNoise.toFixed(2),
          volatility: volatility.toFixed(1),
          isPositive: todayReturn >= 0
        });

      } catch (err) {
        setError("Failed to fetch portfolio data");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolioData();

    // Optional: Refresh every 5 minutes
    const interval = setInterval(fetchPortfolioData, 300000);
    return () => clearInterval(interval);
  }, [ticker, horizon]);

  if (loading) {
    return (
      <div className="portfolioContainer">
        <h2 className="title">Portfolio Performance</h2>
        <div className="loading">Loading portfolio data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolioContainer">
        <h2 className="title">Portfolio Performance</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="portfolioContainer">
      <div className="header">
        <h2 className="title">Portfolio Performance ({ticker})</h2>
        <div className="timeSelector">
          {[5, 10, 20].map(days => (
            <button
              key={days}
              className={horizon === days ? "activeButton" : "button"}
              onClick={() => setHorizon(days)}
            >
              {days}D
            </button>
          ))}
        </div>
      </div>

      <div className="metrics">
        <div className="metricRow">
          <span className="metricLabel">Predicted Return:</span>
          <span className={metrics?.isPositive ? "positiveValue" : "negativeValue"}>
            {metrics?.isPositive ? '+' : ''}{metrics?.todayReturn}%
          </span>
        </div>
        <div className="metricRow">
          <span className="metricLabel">Signal Strength:</span>
          <span className="metricValue">{metrics?.sharpeRatio}</span>
        </div>
        <div className="metricRow">
          <span className="metricLabel">Volatility:</span>
          <span className="metricValue">{metrics?.volatility}%</span>
        </div>
      </div>

      <div className="chartWrapper">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="date" stroke="#aaa" />
            <YAxis stroke="#aaa" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}