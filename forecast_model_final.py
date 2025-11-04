#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error

def load_and_prepare(parquet_path):
    df = pd.read_parquet(parquet_path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "timestamp" in df.columns: df = df.rename(columns={"timestamp":"date"})
    if "symbol" in df.columns:    df = df.rename(columns={"symbol":"ticker"})
    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError({"columns": list(df.columns)})
    if "ticker" not in df.columns:
        df["ticker"] = "UNK"
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date","ticker","close"]).sort_values(["ticker","date"])
    return df

def make_supervised(series, n_lags):
    df = pd.DataFrame({"y": series.values})
    for k in range(1, n_lags+1):
        df[f"lag_{k}"] = df["y"].shift(k)
    df = df.dropna().reset_index(drop=True)
    X = df[[f"lag_{k}" for k in range(1, n_lags+1)]].values
    y = df["y"].values
    return X, y

def fit_pipe(X, y):
    pipe = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
    pipe.fit(X, y)
    return pipe

def forecast_recursive(last_values, model, n_steps):
    preds = []
    buf = list(last_values.astype(float))
    for _ in range(n_steps):
        x = np.array(buf[-len(last_values):][::-1])  # lag_1=most recent
        yhat = float(model.predict(x.reshape(1, -1))[0])
        preds.append(yhat)
        buf.append(yhat)
    return np.array(preds)

def backtest_rmse(close: pd.Series, n_lags: int, n_splits: int = 5) -> float:
    """TimeSeriesSplit CV to estimate *daily* RMSE for uncertainty."""
    X, y = make_supervised(close.astype(float), n_lags)
    if len(X) < max(10, n_splits + 5):
        # Fallback (short history): use std of first differences
        diffs = np.diff(y)
        return float(np.nan_to_num(np.std(diffs), nan=0.0))
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmses = []
    for tr, te in tscv.split(X):
        pipe = fit_pipe(X[tr], y[tr])
        pred = pipe.predict(X[te])
        rmses.append(np.sqrt(mean_squared_error(y[te], pred)))
    return float(np.mean(rmses)) if len(rmses) else 0.0

def evaluate_decision(last_close: float, y_pred: np.ndarray, rmse_day: float, horizon: int) -> dict:
    """Rules: need >=2 true to BUY.
       1) R_h > 2 * uncert
       2) slope > 0 and R_h > 3%
       3) predicted max drawdown < 2.5%
    """
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

    # Positioning and risk bands
    position = float(min(1.0, max(0.0, R_h/(3*uncert)))) if (buy and uncert>0) else 0.0
    stop_loss = -uncert
    take_profit = 2 * uncert

    return {
        "pred_return_h": R_h,
        "uncert_h": uncert,
        "signal_to_noise": (R_h/uncert) if uncert>0 else float("inf"),
        "slope_pred": slope,
        "max_drawdown_pred": max_dd_pred,
        "buy": bool(buy),
        "suggested_position_0to1": position,
        "stop_loss_rel": stop_loss,
        "take_profit_rel": take_profit
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True, help="symbol in your data, e.g. AAMI / ZWS")
    ap.add_argument("--parquet", default="./stock_data_since_2016.parquet")
    ap.add_argument("--lags", type=int, default=10, help="number of close lags as features")
    ap.add_argument("--horizon", type=int, default=20, help="forecast steps (business days)")
    ap.add_argument("--per_rows", type=int, default=5000, help="use last N rows for speed")
    ap.add_argument("--out_csv", default=None)
    ap.add_argument("--save_decision_json", default=None,
                    help="Optional path to save the decision report as JSON (e.g., decision_AAMI.json)")
    ap.add_argument("--no_plot", action="store_true", help="Disable matplotlib plotting")
    args = ap.parse_args()

    df = load_and_prepare(args.parquet)
    if args.ticker not in set(df["ticker"].unique()):
        sample = df["ticker"].drop_duplicates().head(20).tolist()
        raise SystemExit(f"ticker '{args.ticker}' not found. sample: {sample}")

    g = df[df["ticker"] == args.ticker].copy()
    if args.per_rows and args.per_rows > 0:
        g = g.tail(args.per_rows)

    close = g["close"].astype(float)
    if len(close) <= args.lags + 5:
        raise SystemExit("not enough history for the chosen lags.")

    X, y = make_supervised(close, args.lags)
    pipe = fit_pipe(X, y)

    last_lags = close.tail(args.lags).values[::-1]  # lag_1=most recent
    preds = forecast_recursive(last_lags, pipe, args.horizon)

    last_date = pd.to_datetime(g["date"].iloc[-1]).normalize()
    future_dates = pd.bdate_range(last_date + pd.Timedelta(days=1), periods=args.horizon)

    out = pd.DataFrame({"date": future_dates, "ticker": args.ticker, "pred_close": preds})
    save_path = args.out_csv or f"forecast_{args.ticker}.csv"
    out.to_csv(save_path, index=False)
    print(f"Saved forecast -> {save_path}")
    print(out.head(10).to_string(index=False))

    # --- New: backtest + decision ---
    rmse_day = backtest_rmse(close, args.lags)
    report = evaluate_decision(float(close.iloc[-1]), preds, rmse_day, args.horizon)

    print("\n=== DECISION REPORT ===")
    print(f"{'ticker':>22}: {args.ticker}")
    print(f"{'last_close':>22}: {float(close.iloc[-1])}")
    print(f"{'pred_last':>22}: {float(preds[-1])}")
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
            json.dump({
                "ticker": args.ticker,
                "last_close": float(close.iloc[-1]),
                "pred_last": float(preds[-1]),
                **report
            }, f, ensure_ascii=False, indent=2)
        print(f"Saved decision JSON -> {args.save_decision_json}")

    # Optional: forecast plot
    if not args.no_plot:
        plt.figure(figsize=(10,5))
        plt.plot(out["date"], out["pred_close"], label=f"Forecast({args.ticker})", linewidth=2)
        plt.title(f"Forecast Close (next {args.horizon} business days) — {args.ticker}")
        plt.xlabel("Date"); plt.ylabel("Predicted Close"); plt.legend(); plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
