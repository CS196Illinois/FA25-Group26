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

export default function PortfolioPerformance() {
  const [chartData, setChartData] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [horizon, setHorizon] = useState(5);
  const [selectedTicker, setSelectedTicker] = useState("PORTFOLIO");

  // Popular stocks available in the dataset
  const portfolioStocks = ["AAPL", "MSFT", "TSLA", "NVDA"];
  const availableOptions = ["PORTFOLIO", ...portfolioStocks, "GOOGL", "AMZN", "META", "NFLX"];

  useEffect(() => {
    const fetchPortfolioData = async () => {
      setLoading(true);
      setError(null);

      try {
        if (selectedTicker === "PORTFOLIO") {
          // Fetch data for all portfolio stocks
          const promises = portfolioStocks.map(ticker =>
            getDetailedForecast(ticker, horizon, 10).catch(err => {
              console.log(`Skipping ${ticker}: ${err.message}`);
              return null;
            })
          );

          const results = await Promise.all(promises);
          const validResults = results.filter(r => r !== null);

          if (validResults.length === 0) {
            setError("Failed to fetch portfolio data");
            return;
          }

          // Calculate average metrics across portfolio
          const avgReturn = validResults.reduce((sum, r) => sum + r.decision.pred_return_h, 0) / validResults.length;
          const avgUncertainty = validResults.reduce((sum, r) => sum + r.decision.uncert_h, 0) / validResults.length;
          const avgSignalToNoise = validResults.reduce((sum, r) => sum + r.decision.signal_to_noise, 0) / validResults.length;

          // Aggregate forecast data by averaging prices for each date
          const dateMap = {};
          validResults.forEach(result => {
            result.forecast.forEach(item => {
              if (!dateMap[item.date]) {
                dateMap[item.date] = { sum: 0, count: 0 };
              }
              dateMap[item.date].sum += item.pred_close;
              dateMap[item.date].count += 1;
            });
          });

          const transformedData = Object.keys(dateMap).sort().map(date => {
            const d = new Date(date);
            const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            return {
              date: dayNames[d.getDay()],
              value: dateMap[date].sum / dateMap[date].count,
              fullDate: date
            };
          });

          setChartData(transformedData);
          setMetrics({
            todayReturn: (avgReturn * 100).toFixed(2),
            sharpeRatio: avgSignalToNoise.toFixed(2),
            volatility: (avgUncertainty * 100).toFixed(1),
            isPositive: avgReturn >= 0
          });

        } else {
          // Fetch data for single stock
          const forecast = await getDetailedForecast(selectedTicker, horizon, 10);

          // Transform forecast data for the chart
          const transformedData = forecast.forecast.map((item) => {
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

          setMetrics({
            todayReturn: (predictedReturn * 100).toFixed(2),
            sharpeRatio: signalToNoise.toFixed(2),
            volatility: (uncertainty * 100).toFixed(1),
            isPositive: predictedReturn >= 0
          });
        }

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
  }, [selectedTicker, horizon]);

  // Calculate Y-axis domain based on data
  const getYAxisDomain = () => {
    if (chartData.length === 0) return ['auto', 'auto'];

    const values = chartData.map(d => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const padding = (max - min) * 0.1; // 10% padding

    return [
      (min - padding).toFixed(2),
      (max + padding).toFixed(2)
    ];
  };

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
        <h2 className="title">Portfolio Performance</h2>
        <div className="controls">
          <select
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            className="stockSelector"
          >
            <option value="PORTFOLIO">📊 Full Portfolio</option>
            <optgroup label="Individual Stocks">
              {portfolioStocks.map(stock => (
                <option key={stock} value={stock}>{stock}</option>
              ))}
            </optgroup>
            <optgroup label="Other Stocks">
              {availableOptions.filter(s => s !== "PORTFOLIO" && !portfolioStocks.includes(s)).map(stock => (
                <option key={stock} value={stock}>{stock}</option>
              ))}
            </optgroup>
          </select>
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
            <YAxis
              stroke="#aaa"
              domain={getYAxisDomain()}
              tickFormatter={(value) => value.toFixed(2)}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
              formatter={(value) => value.toFixed(2)}
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
