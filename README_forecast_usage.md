# 📘 Usage Guide - forecast_close_final_plus.py

## Step 1: Forecast and Print Buy/Hold Recommendation
```bash
python3 forecast_close_final_plus.py --ticker AAMI --lags 10 --horizon 20
```
- Loads stock data from `stock_data_since_2016.parquet`.
- Uses 10 lag days as features to train a linear regression model.
- Forecasts the next 20 business days for ticker **AAMI**.
- Prints forecasted prices and a Buy/Hold recommendation to the console.
- Saves the forecast results as `forecast_AAMI.csv`.

---

## Step 2: Forecast and Save Full Decision Report
```bash
python3 forecast_close_final_plus.py --ticker AAMI --lags 10 --horizon 20 --save_decision_json decision_AAMI.json
```
- Performs the same forecast and recommendation as Step 1.
- Additionally saves a detailed decision report to `decision_AAMI.json`.

### Decision Report Fields
| Field | Description |
|--------|--------------|
| **ticker** | Stock symbol |
| **last_close** | Latest closing price |
| **pred_last** | Predicted price on the last forecast day |
| **pred_return_h** | Predicted cumulative return |
| **uncert_h** | Forecast uncertainty |
| **signal_to_noise** | Signal-to-noise ratio = Return / Uncertainty |
| **slope_pred** | Forecast trend slope |
| **max_drawdown_pred** | Predicted maximum drawdown |
| **buy** | Buy recommendation (Boolean) |
| **suggested_position_0to1** | Suggested position size (0–1) |
| **stop_loss_rel / take_profit_rel** | Relative stop loss / take profit thresholds |

---

## Example
```bash
# Basic forecast and recommendation
python3 forecast_close_final_plus.py --ticker AAMI --lags 10 --horizon 20

# Forecast + save decision report
python3 forecast_close_final_plus.py --ticker AAMI --lags 10 --horizon 20 --save_decision_json decision_AAMI.json
```
