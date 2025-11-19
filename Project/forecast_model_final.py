#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error


def load_and_prepare(parquet_path: str) -> pd.DataFrame:
    """Load parquet data and normalize key columns."""
    df = pd.read_parquet(parquet_path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "timestamp" in df.columns:
        df = df.rename(columns={"timestamp": "date"})
    if "symbol" in df.columns:
        df = df.rename(columns={"symbol": "ticker"})
    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError({"columns": list(df.columns)})
    if "ticker" not in df.columns:
        df["ticker"] = "UNK"
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "ticker", "close"]).sort_values(["ticker", "date"])
    return df


def make_supervised(series: pd.Series, n_lags: int):
    """Convert close series into supervised learning format."""
    df = pd.DataFrame({"y": series.values})
    for k in range(1, n_lags + 1):
        df[f"lag_{k}"] = df["y"].shift(k)
    df = df.dropna().reset_index(drop=True)
    X = df[[f"lag_{k}" for k in range(1, n_lags + 1)]].values
    y = df["y"].values
    return X, y


def fit_pipe(X, y) -> Pipeline:
    """Fit regression pipeline."""
    pipe = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
    pipe.fit(X, y)
    return pipe


def forecast_recursive(last_values: np.ndarray, model: Pipeline, n_steps: int) -> np.ndarray:
    """Generate multi-step forecasts recursively."""
    preds: List[float] = []
    buf = list(last_values.astype(float))
    for _ in range(n_steps):
        x = np.array(buf[-len(last_values):][::-1])
        yhat = float(model.predict(x.reshape(1, -1))[0])
        preds.append(yhat)
        buf.append(yhat)
    return np.array(preds)


def backtest_rmse(close: pd.Series, n_lags: int, n_splits: int = 5) -> float:
    """Estimate daily RMSE via time-series CV."""
    X, y = make_supervised(close.astype(float), n_lags)
    if len(X) < max(10, n_splits + 5):
        diffs = np.diff(y)
        return float(np.nan_to_num(np.std(diffs), nan=0.0))
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmses = []
    for tr, te in tscv.split(X):
        pipe = fit_pipe(X[tr], y[tr])
        pred = pipe.predict(X[te])
        rmses.append(np.sqrt(mean_squared_error(y[te], pred)))
    return float(np.mean(rmses)) if len(rmses) else 0.0


def evaluate_decision(last_close: float, y_pred: np.ndarray, rmse_day: float, horizon: int) -> Dict[str, Any]:
    """Generate a simple trading decision report."""
    R_h = float(y_pred[-1] / last_close - 1.0)
    uncert = float(np.sqrt(horizon) * rmse_day / last_close) if last_close > 0 else 0.0
    slope = float(np.polyfit(np.arange(len(y_pred)), y_pred, 1)[0])
    s = pd.Series(y_pred)
    dd = (s.cummax() - s) / s.cummax()
    max_dd_pred = float(dd.max()) if len(s) else 0.0

    cond1 = R_h > 2 * uncert
    cond2 = (slope > 0) and (R_h > 0.03)
    cond3 = (max_dd_pred < 0.025)
    buy = sum([cond1, cond2, cond3]) >= 2

    position = float(min(1.0, max(0.0, R_h / (3 * uncert)))) if (buy and uncert > 0) else 0.0
    stop_loss = -uncert
    take_profit = 2 * uncert

    return {
        "pred_return_h": R_h,
        "uncert_h": uncert,
        "signal_to_noise": (R_h / uncert) if uncert > 0 else float("inf"),
        "slope_pred": slope,
        "max_drawdown_pred": max_dd_pred,
        "buy": bool(buy),
        "suggested_position_0to1": position,
        "stop_loss_rel": stop_loss,
        "take_profit_rel": take_profit,
    }


def run_forecast(
    ticker: str,
    parquet_path: str = "./stock_data_since_2016.parquet",
    lags: int = 10,
    horizon: int = 20,
    per_rows: int = 5000,
) -> Dict[str, Any]:
    """Main callable function for API/frontend use."""
    df = load_and_prepare(parquet_path)

    if ticker not in set(df["ticker"].unique()):
        sample = df["ticker"].drop_duplicates().head(20).tolist()
        raise ValueError(f"ticker '{ticker}' not found. sample: {sample}")

    g = df[df["ticker"] == ticker].copy()
    if per_rows and per_rows > 0:
        g = g.tail(per_rows)

    close = g["close"].astype(float)
    if len(close) <= lags + 5:
        raise ValueError("not enough history for the chosen lags.")

    X, y = make_supervised(close, lags)
    pipe = fit_pipe(X, y)

    last_lags = close.tail(lags).values[::-1]
    preds = forecast_recursive(last_lags, pipe, horizon)

    last_date = pd.to_datetime(g["date"].iloc[-1]).normalize()
    future_dates = pd.bdate_range(last_date + pd.Timedelta(days=1), periods=horizon)

    rmse_day = backtest_rmse(close, lags)
    decision_report = evaluate_decision(float(close.iloc[-1]), preds, rmse_day, horizon)

    forecast_list = [
        {
            "date": d.isoformat(),
            "ticker": ticker,
            "pred_close": float(p),
        }
        for d, p in zip(future_dates, preds)
    ]

    return {
        "ticker": ticker,
        "last_close": float(close.iloc[-1]),
        "pred_last": float(preds[-1]),
        "horizon": horizon,
        "lags": lags,
        "forecast": forecast_list,
        "decision": decision_report,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--parquet", default="./stock_data_since_2016.parquet")
    ap.add_argument("--lags", type=int, default=10)
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--per_rows", type=int, default=5000)
    ap.add_argument("--out_csv", default=None)
    ap.add_argument("--save_decision_json", default=None)
    ap.add_argument("--no_plot", action="store_true")
    args = ap.parse_args()

    result = run_forecast(
        ticker=args.ticker,
        parquet_path=args.parquet,
        lags=args.lags,
        horizon=args.horizon,
        per_rows=args.per_rows,
    )

    import os

    forecast_df = pd.DataFrame(result["forecast"])
    save_path = args.out_csv or f"forecast_{args.ticker}.csv"
    forecast_df.to_csv(save_path, index=False)
    print(f"Saved forecast -> {os.path.abspath(save_path)}")
    print(forecast_df.head(10).to_string(index=False))

    report = result["decision"]
    print("\n=== DECISION REPORT ===")
    print(f"{'ticker':>22}: {result['ticker']}")
    print(f"{'last_close':>22}: {result['last_close']}")
    print(f"{'pred_last':>22}: {result['pred_last']}")
    print(f"{'pred_return_h':>22}: {report['pred_return_h']}")
    print(f"{'uncert_h':>22}: {report['uncert_h']}")
    print(f"{'signal_to_noise':>22}: {report['signal_to_noise']}")
    print(f"{'slope_pred':>22}: {report['slope_pred']}")
    print(f"{'max_drawdown_pred':>22}: {report['max_drawdown_pred']}")
    print(f"{'buy':>22}: {report['buy']}")
    print(f"{'suggested_position_0to1':>22}: {report['suggested_position_0to1']}")
    print(f"{'stop_loss_rel':>22}: {report['stop_loss_rel']}")
    print(f"{'take_profit_rel':>22}: {report['take_profit_rel']}")

    if args.save_decision_json:
        with open(args.save_decision_json, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "ticker": result["ticker"],
                    "last_close": result["last_close"],
                    "pred_last": result["pred_last"],
                    **report,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"Saved decision JSON -> {args.save_decision_json}")

    if not args.no_plot:
        plt.figure(figsize=(10, 5))
        plt.plot(
            [pd.to_datetime(r["date"]) for r in result["forecast"]],
            [r["pred_close"] for r in result["forecast"]],
            label=f"Forecast({result['ticker']})",
            linewidth=2,
        )
        plt.title(f"Forecast Close (next {result['horizon']} business days) — {result['ticker']}")
        plt.xlabel("Date")
        plt.ylabel("Predicted Close")
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()