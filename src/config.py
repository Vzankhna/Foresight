from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"

SALES_FILE = RAW_DIR / "sales_daily.csv"
SKU_FILE = RAW_DIR / "sku_master.csv"
CALENDAR_FILE = RAW_DIR / "calendar.csv"
INVENTORY_FILE = RAW_DIR / "inventory_snapshots.csv"

ANALYSIS_DAILY_FILE = PROCESSED_DIR / "analysis_ready_daily.csv"
WEEKLY_FEATURE_FILE = PROCESSED_DIR / "weekly_features.csv"

MODEL_FILE = MODEL_DIR / "foresight_model.jobllib"
FEATURE_COLUMNS_FILE = MODEL_DIR / "feature_columns.json"

FORECAST_FILE = OUTPUT_DIR / "forecast.csv"
RISK_FILE = OUTPUT_DIR / "risk_scores.csv"
METRICS_FILE = OUTPUT_DIR / "model_metrics.json"
QUALITY_FILE = OUTPUT_DIR / "data_quality_report.json"

FORECAST_HORIZON_WEEKS = 8
SEASONAL_LAG = 52
BACKTEST_WEEKS = 8
RANDOM_STATE = 42

for directory in [RAW_DIR, PROCESSED_DIR, MODEL_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)