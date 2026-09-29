from pathlib import Path
import json
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"

@st.cache_data
def load_sales():
    file = DATA_DIR / "analysis_ready_daily.csv"

    if not file.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        file,
        parse_dates = ["Date"]
    )
    return df

@st.cache_data
def load_weekly():
    file = DATA_DIR / "weekly_features.csv"

    if not file.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        file,
        parse_dates = ["week-start"]
    )
    return df

@st.cache_data
def load_forecast():
    file = OUTPUT_DIR / "forecast.csv"

    if not file.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        file,
        parse_dates = ["week_start"]
    )
    return df

@st.cache_data
def load_risk():
    file = OUTPUT_DIR / "risk_scores.csv"

    if not file.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        file,
        parse_dates = ["snapshot_date"] 
    )
    return df

@st.cache_data
def load_sku():
    file = RAW_DIR / "sku_master.csv"

    if not file.exists():
        return pd.DataFrame()
    df = pd.read_csv( file )
    return df

@st.cache_data
def load_calendar():
    file = RAW_DIR / "calendar.csv"

    if not file.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        file,
        parse_dates = ["date"] 
    )
    return df


@st.cache_data
def load_inventory():
    file = RAW_DIR / "inventory_snapshots.csv"

    if not file.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        file,
        parse_dates = ["Snapshot_Date"] 
    )
    return df

@st.cache_data
def load_metrics():
    file = OUTPUT_DIR / "model_metrics.json"

    if not file.exists():
        return {}

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def format_rupees(value):
    if pd.isna(value):
        return "₹0"
    value = float(value)

    if abs(value) >= 10_000_000:
        return f"₹{value / 10_000_000:.2f}Cr"
    if abs(value) >= 100_000:
        return f"₹{value / 100_000:.2f}L"
    if abs(value) >= 1_000:
        return f"₹{value / 1_000:.2f}K"
    return f"₹{value:,.0f}"

def format_number(value):
    if pd.isna(value):
        return "0"
    return f"{float(value):,.0f}"

def check_data():
    sales = load_sales()
    weekly = load_weekly()
    forecast = load_forecast()
    risk = load_risk()

    missing = []

    if sales.empty:
        missing.append("analysis_ready_daily.cvs")
    if weekly.empty:
        missing.append("weekly_features.csv")
    if forecast.empty:
        missing.append("forecast.csv")
    if risk.empty:
        missing.append("risk_scores.csv")

    if missing:
        st.error("Required output files are missing.")
        st.code("python scripts/run_pipeline.py")
        st.write("Missing files:")

        for file in missing:
            st.write(f"- {file}")
        st.stop()