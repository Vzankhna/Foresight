import json
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from src.config import ( WEEKLY_FEATURE_FILE, MODEL_FILE, FEATURE_COLUMNS_FILE, FORECAST_FILE, METRICS_FILE, FORECAST_HORIZON_WEEKS, SEASONAL_LAG, BACKTEST_WEEKS, RANDOM_STATE)

warnings.filterwarnings("ignore")
TARGET = "units_sold"
CATEGORICAL_FEATURES = ["category", "subcategory"]
NUMERIC_FEATURES = ["promo_flag", "is_holiday", "on_hand_units", "on_order_units", "lead_time_days", "safety_stock", "reorder_point", "inventory_value",
    "unit_price", "year", "month", "quarter", "week_of_year", "trend_index", "lag_1", "lag_2", "lag_4", "lag_8", "lag_13", "lag_26", "lag_52",
    "rolling_mean_4", "rolling_mean_8", "rolling_mean_13", "rolling_std_4", "rolling_std_8", "rolling_std_13"
]
FEATURE_COLUMNS = (CATEGORICAL_FEATURES + NUMERIC_FEATURES)

def wape(actual, predicted):
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    denominator = np.sum(np.abs(actual))

    if denominator == 0:
        return 0.0
    return float(np.sum(np.abs(actual - predicted)) / denominator)

def bias(actual, predicted):
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    return float(np.mean(predicted - actual))

def build_model():
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical",OneHotEncoder(handle_unknown="ignore"),CATEGORICAL_FEATURES),
            ("numeric", "passthrough", NUMERIC_FEATURES)
        ]
    )
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )
    return pipeline

def prepare_training_data(df):
    data = df.copy()
    data = data.dropna(subset=FEATURE_COLUMNS + [TARGET])
    data = data.sort_values(["date", "sku"]).reset_index(drop=True)
    return data

def seasonal_backtest(df):
    data = df.copy()
    data["date"] = pd.to_datetime(data["date"],errors="coerce")
    valid = data.dropna(subset=["seasonal_naive", TARGET, "date"]).copy()
    if valid.empty:
        return {
            "wape": None,
            "bias": None
        }
    last_date = valid["date"].max()
    start_date = (last_date - pd.Timedelta(weeks=BACKTEST_WEEKS))
    test = valid[valid["date"] > start_date].copy()
    if test.empty:
        return {
            "wape": None,
            "bias": None
        }
    return {
        "wape": wape(test[TARGET], test["seasonal_naive"]),
        "bias": bias(test[TARGET], test["seasonal_naive"])
    }

def rolling_model_backtest(df):
    data = prepare_training_data(df)
    unique_dates = sorted(data["date"].unique())
    if len(unique_dates) <= (BACKTEST_WEEKS + 10):
        return {
            "wape": None,
            "bias": None
        }
    test_dates = unique_dates[-BACKTEST_WEEKS:]
    predictions = []
    actuals = []

    for test_date in test_dates:
        train = data[data["date"] < test_date]
        test = data[data["date"] == test_date]
        if train.empty or test.empty:
            continue

        model = build_model()
        model.fit(train[FEATURE_COLUMNS], train[TARGET])
        pred = model.predict(test[FEATURE_COLUMNS])
        pred = np.maximum(pred, 0)
        predictions.extend(pred.tolist())
        actuals.extend(test[TARGET].tolist())

    if not actuals:
        return {
            "wape": None,
            "bias": None
        }
    return {
        "wape": wape(actuals,predictions),
        "bias": bias(actuals,predictions)
    }

def train_final_model(df):
    data = prepare_training_data(df)
    if data.empty:
        raise ValueError("No training data available after removing missing feature values.")
    model = build_model()
    model.fit(data[FEATURE_COLUMNS], data[TARGET])
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEATURE_COLUMNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)

    with open(FEATURE_COLUMNS_FILE, "w", encoding="utf-8") as file:
        json.dump(FEATURE_COLUMNS, file, indent=4)
    return model

def create_future_rows(history, sku, horizon):
    history = history.copy()
    rows = []
    sku_history = (history[history["sku"] == sku].sort_values("date"))
    if sku_history.empty:
        return pd.DataFrame()
    last_date = (sku_history["date"].max())
    last_row = sku_history.iloc[-1]

    for step in range(1, horizon + 1):
        future_date = (last_date + pd.Timedelta(weeks=step))
        rows.append({
            "date": future_date,
            "sku": sku,
            "category": last_row["category"],
            "subcategory": last_row["subcategory"],
            "promo_flag": 0,
            "is_holiday": 0,
            "on_hand_units": last_row["on_hand_units"],
            "on_order_units": last_row["on_order_units"],
            "lead_time_days": last_row["lead_time_days"],
            "safety_stock": last_row["safety_stock"],
            "reorder_point": last_row["reorder_point"],
            "inventory_value": last_row["inventory_value"],
            "unit_price": last_row["unit_price"],
            "year": future_date.year,
            "month": future_date.month,
            "quarter": future_date.quarter,
            "week_of_year": int(future_date.isocalendar().week),
            "trend_index": (int(last_row["trend_index"]) + step)
        })
    return pd.DataFrame(rows)

def add_recursive_features(future, history):
    combined = pd.concat([history.copy(), future.copy()], ignore_index=True)
    combined = combined.sort_values(["sku", "date"]).reset_index(drop=True)

    for lag in [1, 2, 4, 8, 13, 26, 52]:
        combined[f"lag_{lag}"] = (
            combined
            .groupby("sku")["units_sold"]
            .shift(lag)
        )
    for window in [4, 8, 13]:
        combined[f"rolling_mean_{window}"] = (
            combined
            .groupby("sku")["units_sold"]
            .transform(lambda x: x.shift(1) .rolling(window,min_periods=1).mean()
            )
        )
        combined[f"rolling_std_{window}"] = (
            combined
            .groupby("sku")["units_sold"]
            .transform(
                lambda x: x.shift(1).rolling(window, min_periods=2).std()
            )
        )
    for column in ["rolling_std_4", "rolling_std_8", "rolling_std_13"]:
        combined[column] = (combined[column].fillna(0))
    return combined

def forecast_skus(model, weekly, horizon=FORECAST_HORIZON_WEEKS):
    history = weekly.copy()
    history["date"] = pd.to_datetime(history["date"], errors="coerce")
    all_forecasts = []

    for sku in sorted(history["sku"].unique()):
        sku_history = (history[history["sku"] == sku]
            .copy()
            .sort_values("date")
        )
        future = create_future_rows(history, sku, horizon)
        if future.empty:
            continue
        for step in range(horizon):
            future_with_features = (add_recursive_features(future, history))
            current = (future_with_features.iloc[[step]].copy())
            available = current.dropna(subset=FEATURE_COLUMNS)

            if available.empty:
                recent_values = (sku_history["units_sold"].tail(4))
                if recent_values.empty:
                    prediction = 0.0
                else:
                    prediction = float(recent_values.mean())
            else:
                prediction = float(model.predict(available[FEATURE_COLUMNS])[0])

            prediction = max(0, prediction)
            future.loc[future.index[step], "units_sold"] = prediction
            history = pd.concat([history, future.iloc[[step]].copy()],ignore_index=True)

        future["forecast_units"] = (future["units_sold"])
        future["forecast_horizon_week"] = np.arange(1, horizon + 1)
        future["forecast_lower"] = (future["forecast_units"] * 0.8)
        future["forecast_upper"] = (future["forecast_units"] * 1.2)

        all_forecasts.append(
            future[["date", "sku", "category", "subcategory", "forecast_horizon_week", "forecast_units", "forecast_lower", "forecast_upper",
                 "on_hand_units", "on_order_units", "lead_time_days", "safety_stock", "reorder_point", "unit_price"]]
        )
    if not all_forecasts:
        return pd.DataFrame()
    return pd.concat(all_forecasts, ignore_index=True)

def run_forecasting():
    weekly = pd.read_csv(WEEKLY_FEATURE_FILE, parse_dates=["date"])
    print("=" * 70)
    print("FORESIGHT FORECASTING")
    print("=" * 70)
    print(f"Weekly rows loaded: {len(weekly):,}")

    baseline_metrics = seasonal_backtest(weekly)
    print("Seasonal Naive WAPE:", baseline_metrics["wape"])
    model_metrics = rolling_model_backtest(weekly)
    print("Random Forest WAPE:", model_metrics["wape"])
    print("Training final Random Forest model...")
    model = train_final_model(weekly)
    print("Final model trained successfully.")
    forecast = forecast_skus(model, weekly, FORECAST_HORIZON_WEEKS)

    if forecast.empty:
        raise ValueError("Forecast generation returned no rows.")
    forecast["model"] = ("Random Forest")
    FORECAST_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    forecast.to_csv(FORECAST_FILE, index=False)

    metrics = {
        "baseline": {"model": "Seasonal Naive", "wape": baseline_metrics["wape"], "bias": baseline_metrics["bias"]},
        "random_forest": {"model": "Random Forest", "wape": model_metrics["wape"], "bias": model_metrics["bias"]},
        "forecast_horizon_weeks": (FORECAST_HORIZON_WEEKS),
        "seasonal_lag_weeks": (SEASONAL_LAG),
        "backtest_weeks": (BACKTEST_WEEKS)
    }

    with open(METRICS_FILE, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)
    print()
    print("Forecast generated:")
    print(FORECAST_FILE)
    print()
    print("Metrics saved:")
    print(METRICS_FILE)
    print()
    print(f"Forecast rows: {len(forecast):,}")
    return forecast, metrics

if __name__ == "__main__":
    run_forecasting()