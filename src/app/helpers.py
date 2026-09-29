from pathlib import Path
import pandas as pd
import streamlit as st
from src.config import(ANALYSIS_DAILY_FILE, WEEKLY_FEATURE_FILE, FORECAST_FILE, RISK_FILE)

@st.cache_data
def load_daily():
    if not ANALYSIS_DAILY_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(ANALYSIS_DAILY_FILE, parse_dates=["date"])

@st.cache_data
def load_weekly():
    if not WEEKLY_FEATURE_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(WEEKLY_FEATURE_FILE, parse_dates=["date"])

@st.cache_data
def load_forecast():
    if not FORECAST_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(FORECAST_FILE)

@st.cache_data
def load_risk():
    if not RISK_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(RISK_FILE)

def format_rupees(value):
    if pd.isna(value):
        return "₹0"
    return f"₹{value:,.0f}"

def format_number(value):
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"

def sidebar_filters(df):
    st.sidebar.header("Filters")
    categories = ["All"]

    if(not df.empty and "category" in df.columns):
        categories += sorted(
            df["category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    category = st.sidebar.selectbox("Category", categories)
    filtered = df.copy()

    if category != "All":
        filtered = filtered[filtered["category"] == category]
    return filtered

def page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)

def require_data(df, message):
    if df.empty:
        st.warning(message)
        st.stop()