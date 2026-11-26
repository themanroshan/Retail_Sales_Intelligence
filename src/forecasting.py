"""Forecasting models and metrics.

Three models compared on daily order volume:
  - Naive          : forecast = last observed value
  - Seasonal Naive : repeat the last 7-day cycle
  - SARIMA         : classic statistical model with weekly seasonality
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


# ---------- MODELS ----------
class NaiveForecaster:
    """Predict the last observed value for the entire horizon."""

    def fit(self, series):
        self.last_value = float(series.iloc[-1])
        self.last_date = series.index[-1]
        return self

    def predict(self, horizon):
        future_index = pd.date_range(
            self.last_date + pd.Timedelta(days=1), periods=horizon, freq="D"
        )
        return pd.Series([self.last_value] * horizon, index=future_index)


class SeasonalNaiveForecaster:
    """Repeat the last 7 days as the forecast pattern."""

    def __init__(self, season_length=7):
        self.season_length = season_length

    def fit(self, series):
        self.history = series.copy()
        return self

    def predict(self, horizon):
        last_cycle = self.history.iloc[-self.season_length:].values
        values = [last_cycle[i % self.season_length] for i in range(horizon)]
        future_index = pd.date_range(
            self.history.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D"
        )
        return pd.Series(values, index=future_index)


class SarimaForecaster:
    """SARIMA(1,1,1)(1,1,1,7) — captures trend + weekly seasonality."""

    def __init__(self, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)):
        self.order = order
        self.seasonal_order = seasonal_order

    def fit(self, series):
        model = SARIMAX(
            series,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        self.model_fit = model.fit(disp=False)
        self.last_date = series.index[-1]
        return self

    def predict(self, horizon):
        forecast = self.model_fit.get_forecast(steps=horizon)
        future_index = pd.date_range(
            self.last_date + pd.Timedelta(days=1), periods=horizon, freq="D"
        )
        return pd.Series(forecast.predicted_mean.values, index=future_index)


# ---------- METRICS ----------
def mae(y_true, y_pred):
    """Mean Absolute Error."""
    return float(np.mean(np.abs(np.array(y_true) - np.array(y_pred))))


def rmse(y_true, y_pred):
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2)))


def wape(y_true, y_pred):
    """Weighted Absolute Percentage Error — robust to zero actuals."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    denom = np.sum(np.abs(y_true))
    if denom == 0:
        return float("nan")
    return float(np.sum(np.abs(y_true - y_pred)) / denom * 100)


def evaluate(y_true, y_pred):
    """Return all metrics as a dict."""
    return {
        "mae": round(mae(y_true, y_pred), 2),
        "rmse": round(rmse(y_true, y_pred), 2),
        "wape": round(wape(y_true, y_pred), 2),
    }


# ---------- DATA SPLIT ----------
def train_test_split(series, train_fraction=0.8):
    """Chronological split — NEVER random for time series."""
    cutoff = int(len(series) * train_fraction)
    return series.iloc[:cutoff], series.iloc[cutoff:]


# ---------- RUN ALL MODELS ----------
def compare_models(series, horizon=None):
    """Fit all three models, return a comparison DataFrame."""
    train, test = train_test_split(series)
    if horizon is None:
        horizon = len(test)

    models = {
        "Naive": NaiveForecaster(),
        "Seasonal Naive": SeasonalNaiveForecaster(season_length=7),
        "SARIMA": SarimaForecaster(),
    }

    results = []
    for name, model in models.items():
        try:
            model.fit(train)
            pred = model.predict(horizon)
            # Align prediction length with test for fair comparison
            pred_aligned = pred.iloc[: len(test)]
            test_aligned = test.iloc[: len(pred_aligned)]
            metrics = evaluate(test_aligned.values, pred_aligned.values)
            results.append({"model": name, **metrics})
        except Exception as e:
            results.append({"model": name, "error": str(e)})

    return pd.DataFrame(results)
