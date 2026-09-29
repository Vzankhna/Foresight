import json
import numpy as np
import pandas as pd
from src.config import (SALES_FILE, SKU_FILE, CALENDAR_FILE, INVENTORY_FILE, ANALYSIS_DAILY_FILE, WEEKLY_FEATURE_FILE, QUALITY_FILE, SEASONAL_LAG)

def clean_columns(df):
    df = df.copy()
    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]
    return df

def load_raw_data():
    sales = pd.read_csv(SALES_FILE)
    sku = pd.read_csv(SKU_FILE)
    calendar = pd.read_csv(CALENDAR_FILE)
    inventory = pd.read_csv(INVENTORY_FILE)

    return sales, sku, calendar, inventory

def clean_sales(sales):
    sales = clean_columns(sales)
    rename_map = {
        "date": "date",
        "sku": "sku",
        "units_sold": "units_sold",
        "revenue": "revenue",
        "price": "unit_price",
        "promotion": "promo_flag"
    }
    sales = sales.rename(columns=rename_map)
    required = [
        "date",
        "sku",
        "units_sold",
        "revenue",
        "unit_price",
        "promo_flag"
    ]
    missing = [column for column in required if column not in sales.columns]

    if missing:
        raise ValueError(f"Sales dataset is missing columns: {missing}")

    sales["date"] = pd.to_datetime(
        sales["date"],
        errors="coerce"
    )
    sales["sku"] = sales["sku"].astype(str).str.strip()
    numeric_columns = [
        "units_sold",
        "revenue",
        "unit_price",
        "promo_flag"
    ]
    for column in numeric_columns:
        sales[column] = pd.to_numeric(
            sales[column],
            errors="coerce"
        )
    sales["units_sold"] = sales["units_sold"].fillna(0).clip(lower=0)
    sales["revenue"] = sales["revenue"].fillna(0).clip(lower=0)
    sales["unit_price"] = sales["unit_price"].fillna(0).clip(lower=0)
    sales["promo_flag"] = sales["promo_flag"].fillna(0).astype(int)
    sales = sales.dropna(subset=["date", "sku"])
    duplicate_count = sales.duplicated(
        subset=["date", "sku"]
    ).sum()
    sales = (
        sales
        .groupby(["date", "sku"], as_index=False)
        .agg({
            "units_sold": "sum",
            "revenue": "sum",
            "unit_price": "mean",
            "promo_flag": "max"
        })
    )
    return sales, int(duplicate_count)

def clean_sku_master(sku):
    sku = clean_columns(sku)
    rename_map = {
        "sku": "sku",
        "product_name": "product_name",
        "category": "category",
        "subcategory": "subcategory",
        "launch_date": "launch_date",
        "cost_price": "cost_price",
        "selling_price": "selling_price",
        "gross_margin_per_unit": "gross_margin_per_unit"
    }
    sku = sku.rename(columns=rename_map)
    required = [
        "sku",
        "product_name",
        "category",
        "subcategory",
        "launch_date",
        "cost_price",
        "selling_price",
        "gross_margin_per_unit"
    ]
    missing = [column for column in required if column not in sku.columns]

    if missing:
        raise ValueError(f"SKU dataset is missing columns: {missing}")

    sku["sku"] = sku["sku"].astype(str).str.strip()
    sku["launch_date"] = pd.to_datetime(
        sku["launch_date"],
        errors="coerce"
    )
    for column in [
        "cost_price",
        "selling_price",
        "gross_margin_per_unit"
    ]:
        sku[column] = pd.to_numeric(
            sku[column],
            errors="coerce"
        )
    sku["category"] = sku["category"].fillna("Unknown")
    sku["subcategory"] = sku["subcategory"].fillna("Unknown")
    sku["product_name"] = sku["product_name"].fillna(sku["sku"])
    sku["cost_price"] = sku["cost_price"].fillna(0)
    sku["selling_price"] = sku["selling_price"].fillna(0)
    sku["gross_margin_per_unit"] = sku[
        "gross_margin_per_unit"
    ].fillna(
        sku["selling_price"] - sku["cost_price"]
    )
    sku = sku.drop_duplicates(subset=["sku"], keep="last")
    return sku

def clean_calendar(calendar):
    calendar = clean_columns(calendar)
    calendar["date"] = pd.to_datetime(
        calendar["date"],
        errors="coerce"
    )
    for column in [
        "year",
        "month",
        "week",
        "day_of_week",
        "is_weekend",
        "season",
        "holiday",
        "is_holiday",
        "promotion_event"
    ]:
        if column not in calendar.columns:
            calendar[column] = np.nan

    calendar["is_holiday"] = pd.to_numeric(
        calendar["is_holiday"],
        errors="coerce"
    ).fillna(0).astype(int)

    calendar["is_weekend"] = pd.to_numeric(
        calendar["is_weekend"],
        errors="coerce"
    ).fillna(0).astype(int)

    calendar["week"] = pd.to_numeric(
        calendar["week"],
        errors="coerce"
    )

    calendar["season"] = calendar["season"].fillna("Unknown")
    calendar["holiday"] = calendar["holiday"].fillna("None")
    calendar["promotion_event"] = calendar["promotion_event"].fillna("None")
    calendar = calendar.dropna(subset=["date"])
    calendar = calendar.drop_duplicates(subset=["date"],keep="last")

    return calendar

def clean_inventory(inventory):
    inventory = clean_columns(inventory)
    rename_map = {
        "snapshot_date": "date",
        "sku": "sku",
        "current_stock": "on_hand_units",
        "on_order": "on_order_units",
        "lead_time_days": "lead_time_days",
        "safety_stock": "safety_stock",
        "reorder_point": "reorder_point",
        "inventory_value": "inventory_value"
    }
    inventory = inventory.rename(columns=rename_map)
    required = [
        "date",
        "sku",
        "on_hand_units",
        "on_order_units",
        "lead_time_days",
        "safety_stock",
        "reorder_point",
        "inventory_value"
    ]
    missing = [
        column
        for column in required
        if column not in inventory.columns
    ]
    if missing:
        raise ValueError(f"Inventory dataset is missing columns: {missing}")

    inventory["date"] = pd.to_datetime(
        inventory["date"],
        errors="coerce"
    )

    inventory["sku"] = inventory[
        "sku"
    ].astype(str).str.strip()

    for column in required[2:]:
        inventory[column] = pd.to_numeric(
            inventory[column],
            errors="coerce"
        )

    for column in required[2:]:
        inventory[column] = inventory[column].fillna(0)

    inventory = inventory.dropna(subset=["date", "sku"])
    inventory = inventory.sort_values(["sku", "date"])
    inventory = inventory.drop_duplicates(subset=["date", "sku"],keep="last")

    return inventory

def build_analysis_daily(sales, sku, calendar, inventory):
    daily = sales.merge(sku, on="sku", how="left")
    daily = daily.merge(calendar, on="date", how="left", suffixes=("", "_calendar"))
    daily = daily.sort_values(["date", "sku"]).reset_index(drop=True)
    inventory_sorted = (
        inventory
        .sort_values(["date", "sku"])
        .reset_index(drop=True)
    )
    daily = pd.merge_asof(daily, inventory_sorted, on="date", by="sku", direction="backward")
    daily["category"] = (daily["category"].fillna("Unknown"))
    daily["subcategory"] = (daily["subcategory"].fillna("Unknown"))
    daily["season"] = (daily["season"].fillna("Unknown"))
    daily["is_holiday"] = (daily["is_holiday"].fillna(0).astype(int))
    daily["promo_flag"] = (daily["promo_flag"].fillna(0).astype(int))

    inventory_columns = [
        "on_hand_units",
        "on_order_units",
        "safety_stock",
        "reorder_point",
        "inventory_value"
    ]

    for column in inventory_columns:
        daily[column] = (daily[column].fillna(0))

    median_lead_time = (daily["lead_time_days"].median())

    if pd.isna(median_lead_time):
        median_lead_time = 0

    daily["lead_time_days"] = (daily["lead_time_days"].fillna(median_lead_time))

    if "gross_margin_per_unit" not in daily.columns:
        daily["gross_margin_per_unit"] = 0

    daily["gross_margin_per_unit"] = (
        pd.to_numeric(
            daily["gross_margin_per_unit"],
            errors="coerce"
        )
        .fillna(0)
    )

    daily["gross_margin"] = (daily["units_sold"] *daily["gross_margin_per_unit"])
    daily = daily.sort_values(["sku", "date"]).reset_index(drop=True)

    return daily

def build_weekly_features(daily):
    weekly = (
        daily
        .set_index("date")
        .groupby("sku")
        .resample("W-SUN")
        .agg({
            "units_sold": "sum",
            "revenue": "sum",
            "promo_flag": "max",
            "is_holiday": "max",
            "on_hand_units": "last",
            "on_order_units": "last",
            "lead_time_days": "last",
            "safety_stock": "last",
            "reorder_point": "last",
            "inventory_value": "last",
            "category": "last",
            "subcategory": "last",
            "unit_price": "mean",
            "gross_margin": "sum"
        })
        .reset_index()
    )

    weekly = weekly.sort_values(["sku", "date"])

    weekly["year"] = weekly["date"].dt.year
    weekly["month"] = weekly["date"].dt.month
    weekly["quarter"] = weekly["date"].dt.quarter
    weekly["week_of_year"] = (weekly["date"].dt.isocalendar().week.astype(int))
    weekly["trend_index"] = (weekly.groupby("sku").cumcount())
    grouped = weekly.groupby("sku")

    for lag in [1, 2, 4, 8, 13, 26, 52]:
        weekly[f"lag_{lag}"] = grouped[
            "units_sold"
        ].shift(lag)

    for window in [4, 8, 13]:
        weekly[f"rolling_mean_{window}"] = (
            grouped["units_sold"]
            .transform(
                lambda x: x.shift(1).rolling(window, min_periods=1).mean()
            )
        )

        weekly[f"rolling_std_{window}"] = (
            grouped["units_sold"]
            .transform(
                lambda x: x.shift(1).rolling(window, min_periods=2).std()
            )
        )

    weekly["rolling_std_4"] = weekly["rolling_std_4"].fillna(0)
    weekly["rolling_std_8"] = weekly["rolling_std_8"].fillna(0)
    weekly["rolling_std_13"] = weekly["rolling_std_13"].fillna(0)
    weekly["seasonal_naive"] = weekly[f"lag_{SEASONAL_LAG}"]
    weekly["promo_rate"] = weekly["promo_flag"]
    weekly["demand_value"] = (weekly["units_sold"] * weekly["unit_price"])
    weekly = weekly.replace([np.inf, -np.inf],np.nan)

    return weekly

def generate_quality_report(sales, sku, calendar, inventory, sales_duplicates):
    report = {
        "sales_rows": int(len(sales)),
        "sku_rows": int(len(sku)),
        "calendar_rows": int(len(calendar)),
        "inventory_rows": int(len(inventory)),
        "sales_duplicate_groups_removed": int(sales_duplicates),
        "sales_missing_values": {
            str(k): int(v)
            for k, v in sales.isna().sum().items()
        },
        "sku_missing_values": {
            str(k): int(v)
            for k, v in sku.isna().sum().items()
        },
        "calendar_missing_values": {
            str(k): int(v)
            for k, v in calendar.isna().sum().items()
        },
        "inventory_missing_values": {
            str(k): int(v)
            for k, v in inventory.isna().sum().items()
        }
    }

    return report

def run_pipeline():
    print("=" * 70)
    print("FORESIGHT DATA PIPELINE")
    print("=" * 70)
    sales_raw, sku_raw, calendar_raw, inventory_raw = load_raw_data()
    print("Raw data loaded.")
    sales, sales_duplicates = clean_sales(sales_raw)
    sku = clean_sku_master(sku_raw)
    calendar = clean_calendar(calendar_raw)
    inventory = clean_inventory(inventory_raw)
    print("Data cleaning completed.")

    daily = build_analysis_daily(sales, sku, calendar, inventory)
    weekly = build_weekly_features(daily)
    daily.to_csv(ANALYSIS_DAILY_FILE, index=False)
    weekly.to_csv(WEEKLY_FEATURE_FILE, index=False)

    quality = generate_quality_report(sales,sku,calendar,inventory,sales_duplicates)

    with open(QUALITY_FILE, "w", encoding="utf-8") as file:
        json.dump(quality, file,indent=4)

    print()
    print("Pipeline completed successfully.")
    print()
    print(f"Daily dataset:")
    print(ANALYSIS_DAILY_FILE)
    print()
    print(f"Weekly feature dataset:")
    print(WEEKLY_FEATURE_FILE)
    print()
    print(f"Quality report:")
    print(QUALITY_FILE)
    print()
    print(f"Daily rows: {len(daily):,}")
    print(f"Weekly rows: {len(weekly):,}")


if __name__ == "__main__":
    run_pipeline()