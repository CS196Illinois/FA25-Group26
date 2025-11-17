from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from forecast_model_final import run_forecast


class ForecastRequest(BaseModel):
    ticker: str
    lags: Optional[int] = 10
    horizon: Optional[int] = 20
    per_rows: Optional[int] = 5000


app = FastAPI(title="Stock Forecast API")


@app.post("/forecast")
def forecast(req: ForecastRequest):
    try:
        result = run_forecast(
            ticker=req.ticker,
            lags=req.lags,
            horizon=req.horizon,
            per_rows=req.per_rows,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
