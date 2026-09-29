import json
import numpy as np
import pandas as pd
from src.config import(FORECAST_FILE, RISK_FILE)

def calculate_risk(forecast):
    forecast = forecast.copy()
    forecast["lead_time_weeks"] = (forecast["lead_time_days"].fillna(7) / 7)
    forecast["weekly_forecast"] = (forecast["forecast_units"])

    summary = (
        forecast
        .groupby("sku")
        .agg(
            category = ("category", "last"),
            subcategory = ("subcategory", "last"),
            on_hand_units = ("on_hand_units", "last"),
            on_order_units = ("on_order_units", "last"),
            lead_time_days = ("lead_time_days", "last"),
            safety_stock = ("safety_stock", "last"),
            reorder_point = ("reorder_point", "last"),
            unit_price = ("unit_price", "last"),
            total_forecast_units = ("forecast_units", "sum"),
            average_weekly_demand = ("forecast_units", "mean")
        )
        .reset_index()
    )
    summary["lead_time_demand"] = (summary["average_weekly_demand"] * summary["lead_time_days"] / 7)
    summary["available_units"] = (summary["on_hand_units"] + summary["on_order_units"])
    summary["stockout_gap"] = (summary["lead_time_demand"] + summary["safety_stock"] - summary["available_units"])
    summary["stockout_risk_score"] = (summary["stockout_gap"] / (summary["lead_time_demand"] + summary["safety_stock"] + 1) * 100)
    summary["stockout_risk_score"] = (summary["stockout_risk_score"].clip(0, 100))
    summary["overstock_units"] = (summary["on_hand_units"] - (summary["total_forecast_units"] * 1.5))
    summary["overstock_risk_score"] = (summary["overstock_units"] / (summary["total_forecast_units"] + 1) * 100)
    summary["overstock_risk_score"] = (summary["overstock_risk_score"].clip(0, 100))
    summary["sales_at_risk"] = (summary["stockout_gap"].clip(lower=0) * summary["unit_price"])
    summary["locked_capital"] = (summary["overstock_units"].clip(lower=0) * summary["unit_price"])
    summary["high_stockout"] = (summary["stockout_risk_score"] >= 30)
    summary["high_overstock"] = (summary["overstock_risk_score"] >= 30)

    def determine_action(row):
        stockout = row["high_stockout"]
        overstock = row["high_overstock"]

        if stockout and not overstock:
            return "Reorder Now"
        if overstock and not stockout:
            return "Markdown / Clear"
        if stockout and overstock:
            return "Watch / Volatile"
        return "Healthy"

    summary["recommended_action"] = (summary.apply(determine_action, axis=1))

    def risk_level(row):
        if(row["high_stockout"] or row["high_overstock"]):
            if(row["stockout_risk_score"] > 70 or row["overstock_risk_score"] >= 70):
                return "High"
            return "Medium"
        return "Low"
    summary["risk_level"] = (summary.apply(risk_level, axis=1))
    return summary

def run_risk_scoring():
    print("=" * 70)
    print("FORESIGHT RISK SCORING")
    print("=" * 70)

    forecast = pd.read_csv(FORECAST_FILE)
    risk = calculate_risk(forecast)
    risk.to_csv(RISK_FILE, index=False)
    totals = {
        "total_skus": int(len(risk)),
        "reorder_now": int((risk["recommended_action"] == "Reorder Now").sum()),
        "markdown_clear": int((risk["recommended_action"] == "Markdown / Clear").sum()),
        "watch_volatile": int((risk["recommended_action"] == "Watch / Volatile").sum()),
        "healthy": int((risk["recommended_action"] == "Healthy").sum()),
        "sales_at_risk": float(risk["sales_at_risk"].sum()),
        "locked_capital": float(risk["locked_capital"].sum())
    }
    print()
    print("Risk file generated")
    print(RISK_FILE)
    print()
    print(json.dumps(totals, indent=4))

    return risk

if __name__ == "__main__":
    run_risk_scoring()