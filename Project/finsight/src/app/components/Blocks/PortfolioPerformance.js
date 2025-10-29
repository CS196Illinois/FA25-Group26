"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

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
    <div
      style={{
        backgroundColor: "#1e1e1e",
        color: "white",
        padding: "20px",
        borderRadius: "12px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
        height: "400px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      {/* Top half: Portfolio metrics (3 rows, left/right aligned) */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          marginBottom: "10px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <strong>Today's Return:</strong>
          <span style={{ color: "#4caf50" }}>+0.55%</span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <strong>Sharpe Ratio:</strong>
          <span>0.85</span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <strong>Volatility:</strong>
          <span>12.5%</span>
        </div>
      </div>

      {/* Optional divider */}
      <hr style={{ border: "1px solid #333", margin: "10px 0" }} />

      {/* Bottom half: Line Chart */}
      <div style={{ flex: 1 }}>
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
