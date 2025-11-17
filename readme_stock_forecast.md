# Stock Forecast Model & API






##  Quick Start

### 1. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, install manually:

```bash
python3 -m pip install fastapi uvicorn scikit-learn pandas numpy "pydantic<3"
```

---

### 2. Start the API server

```bash
python3 -m uvicorn api_server:app --reload --port 8000
```

If successful, you’ll see:

```
Uvicorn running on http://127.0.0.1:8000
```

---

### 3. Open Swagger UI

FastAPI automatically provides an interactive documentation page:

 **http://127.0.0.1:8000/docs**

You can test the API directly from the browser — just click `POST /forecast`, enter a ticker symbol (e.g. `AAPL`), and hit **Execute**.

---

##  Forecast API

### Endpoint

```
POST /forecast
```

### Request Body Example

```json
{
  "ticker": "AAPL",
  "lags": 10,
  "horizon": 20,
  "per_rows": 5000
}
```

Only `ticker` is required; others are optional.

---

### Example Response

```json
{
  "ticker": "AAPL",
  "last_close": 123.45,
  "pred_last": 130.12,
  "forecast": [
    { "date": "2024-01-02T00:00:00", "ticker": "AAPL", "pred_close": 124.01 },
    { "date": "2024-01-03T00:00:00", "ticker": "AAPL", "pred_close": 125.10 }
  ],
  "decision": {
    "pred_return_h": 0.05,
    "uncert_h": 0.02,
    "signal_to_noise": 2.5,
    "slope_pred": 0.1,
    "max_drawdown_pred": 0.01,
    "buy": true,
    "suggested_position_0to1": 0.8,
    "stop_loss_rel": -0.02,
    "take_profit_rel": 0.04
  }
}
```

---


##  Frontend Integration

Frontend can call the API directly using `fetch`, `axios`, or any HTTP client.

### Example (JavaScript)

```js
async function callForecast() {
  const res = await fetch("http://127.0.0.1:8000/forecast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker: "AAPL" })
  });

  const data = await res.json();
  console.log("Forecast:", data.forecast);
  console.log("Decision:", data.decision);
}
```

### Example (React Component)

```jsx
import { useState } from "react";

export default function ForecastWidget() {
  const [ticker, setTicker] = useState("AAPL");
  const [data, setData] = useState(null);

  const fetchData = async () => {
    const res = await fetch("http://127.0.0.1:8000/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker })
    });
    const json = await res.json();
    setData(json);
  };

  return (
    <div>
      <h2>Stock Forecast</h2>
      <input value={ticker} onChange={(e) => setTicker(e.target.value)} />
      <button onClick={fetchData}>Run Forecast</button>

      {data && (
        <>
          <p>Last close: {data.last_close}</p>
          <p>Predicted last: {data.pred_last}</p>
          <p>
            Decision: {" "}
            <strong style={{ color: data.decision.buy ? "green" : "gray" }}>
              {data.decision.buy ? "BUY" : "HOLD"}
            </strong>
          </p>
        </>
      )}
    </div>
  );
}
```

---




- macOS users should always use `python3 -m pip` instead of `pip`  



