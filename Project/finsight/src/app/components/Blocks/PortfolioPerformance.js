"use client";
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
  const data = [
    { date: "Mon", value: 10000 },
    { date: "Tue", value: 10080 },
    { date: "Wed", value: 10150 },
    { date: "Thu", value: 10100 },
    { date: "Fri", value: 10200 },
  ];

  return (
    <div className="portfolioContainer">
      <h2 className="title">Portfolio Performance</h2>

      <div className="metrics">
        <div className="metricRow">
          <span className="metricLabel">Today's Return:</span>
          <span className="positiveValue">+0.55%</span>
        </div>
        <div className="metricRow">
          <span className="metricLabel">Sharpe Ratio:</span>
          <span className="metricValue">0.85</span>
        </div>
        <div className="metricRow">
          <span className="metricLabel">Volatility:</span>
          <span className="metricValue">12.5%</span>
        </div>
      </div>

      <div className="chartWrapper">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="date" stroke="#aaa" />
            <YAxis stroke="#aaa" />
            <Tooltip />
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
