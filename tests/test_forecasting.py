"""Tests for forecasting models and metrics."""

import numpy as np
import pandas as pd
import pytest

from src.forecasting import (
    NaiveForecaster,
    SeasonalNaiveForecaster,
    evaluate,
    mae,
    rmse,
    train_test_split,
    wape,
)


@pytest.fixture
def daily_series():
    """A 40-day series with a weekly pattern."""
    idx = pd.date_range("2024-01-01", periods=40, freq="D")
    values = np.array([100, 110, 120, 130, 140, 130, 110] * 6)[:40]
    return pd.Series(values, index=idx)


def test_naive_forecaster(daily_series):
    f = NaiveForecaster().fit(daily_series)
    pred = f.predict(5)
    assert len(pred) == 5
    assert (pred == daily_series.iloc[-1]).all()


def test_seasonal_naive_forecaster(daily_series):
    f = SeasonalNaiveForecaster(season_length=7).fit(daily_series)
    pred = f.predict(14)
    # First 7 predictions should equal the last 7 historical values
    np.testing.assert_array_equal(pred.values[:7], daily_series.values[-7:])


def test_mae():
    assert mae([10, 20], [12, 18]) == pytest.approx(2.0)


def test_rmse():
    assert rmse([10, 20], [12, 18]) == pytest.approx(2.0)


def test_wape():
    # |10-12| + |20-18| = 4,   |10| + |20| = 30 → 4/30 * 100
    assert wape([10, 20], [12, 18]) == pytest.approx(4 / 30 * 100)


def test_evaluate_returns_all_metrics():
    metrics = evaluate([10, 20, 30], [11, 19, 32])
    assert set(metrics.keys()) == {"mae", "rmse", "wape"}


def test_train_test_split_proportions(daily_series):
    train, test = train_test_split(daily_series, train_fraction=0.75)
    assert len(train) == 30
    assert len(test) == 10
    # Chronological: train must come before test
    assert train.index[-1] < test.index[0]
