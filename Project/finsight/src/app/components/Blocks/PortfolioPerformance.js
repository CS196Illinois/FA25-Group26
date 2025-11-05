"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import styles from "./Portfolio.module.css";

export default function PortfolioPerformance() {
  // Fake portfolio performance data
  const data = [
    { date: "Mon", value: 10000 },
    { date: "Tue", value: 10080 },
    { date: "Wed", value: 10150 },
    { date: "Thu", value: 10100 },
    { date: "Fri", value: 10200 },
  ];

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Portfolio Performance</h2>
      <div className={styles.metricsContainer}>
        <div className={styles.metricRow}>
          <strong>Today's Return:</strong>
          <span className={styles.positiveValue}>+0.55%</span>
        </div>

        <div className={styles.metricRow}>
          <strong>Sharpe Ratio:</strong>
          <span>0.85</span>
        </div>

        <div className={styles.metricRow}>
          <strong>Volatility:</strong>
          <span>12.5%</span>
        </div>
      </div>

      {/* Divider */}
      <hr className={styles.divider} />

      {/* Bottom half: Line Chart */}
      <div className={styles.chartContainer}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="date" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#4caf50"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}