import json
import streamlit as st
from src.app.helpers import(load_risk, page_header, require_data, format_rupees, format_number)
from src.config import METRICS_FILE

page_header(
    "Executive Summary",
    "Decision-focused summary for Operations and Finance"
)
risk = load_risk()
require_data(risk, "Risk data is unavailable.")
sales_at_risk = risk["sales_at_risk"].sum()
locked_capital = risk["locked_capital"].sum()
reorder = (risk["recommended_action"] == "Reorder Now").sum()
clear = (risk["recommended_action"] == "Markdown / Clear").sum()
watch = (risk["recommended_action"] == "Watch / Volatile").sum()
healthy = (risk["recommended_action"] == "Healthy").sum()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Revenue Protection")
    st.metric("Sales at Risk", format_rupees(sales_at_risk))
    st.write(f"{reorder} SKUs are flagged for reorder review.")

with col2:
    st.subheader("Working Capital")
    st.metric("Locked Capital", format_rupees(locked_capital))
    st.write(f"{clear} SKUs are flagged for markdown / clearance review.")

st.divider()
st.subheader("Operational Actions")
st.write(f"Reorder review: {reorder} SKUs")
st.write(f"Markdown / clearance review: {clear} SKUS")
st.write(f"Manual investigation: {watch} SKUs")
st.write(f"Healthy inventory: {healthy} SKUs")

st.divider()
if METRICS_FILE.exists():
    with open(METRICS_FILE, "r", encoding="utf-8") as file:
        metrics = json.load(file)

    st.subheader("Forecast Model Performance")
    baseline = metrics.get("baseline", {})
    rf= metrics.get("random_forest", {})

c1, c2 = st.columns(2)
c1.metric(
    "Seasonal Naive WAPE",
    (
        f"{baseline.get('wape', 0) * 100:.2f}%"
        if baseline.get("wape") is not None else "N/A"
    )
)
c2.metric(
    "Random Forest WAPE",
    (
        f"{rf.get('wape', 0) * 100:.2f}%"
        if rf.get("wape") is not None else "N/A"
    )
)
st.info(
    "Model selection should be based on the "
    "rolling backtest comparison with the "
    "seasonal-naive baseline"
)

st.divider()
st.subheader("Management Review Questions")
st.write("1. Which SKUs require replenishment review?")
st.write("2. Which SKUs have excess inventory?")
st.write("3. How much revenue is exposed to stockout risk?")
st.write("4. How much capital is tied up in overstock?")
st.write("5. Is the forecasting model outperforming the baseline?")