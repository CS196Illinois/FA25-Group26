import React from "react";
import "./MLStockRecommendations.css";

export default function MLStockRecommendations() {
  const recommendations = [
    { symbol: "TSLA", change: "+8.5%", action: "Buy" },
    { symbol: "MSFT", change: "+5%", action: "Hold" },
    { symbol: "AAPL", change: "-3.4%", action: "Sell" },
    { symbol: "JPM", change: "-11.5%", action: "Sell" },
    { symbol: "NVDA", change: "+3.1%", action: "Hold" },
    { symbol: "BABA", change: "-7.4%", action: "Sell" },
    { symbol: "ADBE", change: "-1.1%", action: "Hold" },
    { symbol: "CAT", change: "+9.7%", action: "Buy" },
  ];

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
