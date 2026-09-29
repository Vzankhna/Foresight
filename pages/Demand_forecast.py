import streamlit as st
import plotly.express as px
from src.app.helpers import(load_weekly, load_forecast, page_header, require_data, format_number)

page_header(
    "Demand Forecast",
    "8-week SKU-level demand forecast"
)
weekly = load_weekly()
forecast = load_forecast()
require_data(weekly, "Weekly features are unavailable")
require_data(forecast, "Forecast is unavailable. Run forecasting first.")

sku_list = sorted(
    forecast["sku"]
    .unique()
    .tolist()
)
selected_sku = st.selectbox(
    "Select_SKU",
    sku_list
)
history = weekly[weekly["sku"] == selected_sku].sort_values("date")
future = forecast[forecast["sku"] == selected_sku].sort_values("date")

history_plot = history[
    ["date", "units_sold"]
].rename(columns={"units_sold": "demand"})

future_plot = future[
    ["date", "forecast_units"]
].rename(columns={"forecast_units": "demand"})

history_plot["type"] = "Actual"
future_plot["type"] = "Forecast"

combined = history_plot[["date", "demand", "type"]].tail(52)
combined = __import__("pandas").concat([combined, future_plot[["date", "demand", "type"]]])

fig = px.line(
    combined,
    x="date",
    y="demand",
    color="type",
    markers=True,
    title=f"Demand Forecast — {selected_sku}"
)
st.plotly_chart(
    fig,
    use_container_width=True
)
total_forecast = future["forecast_units"].sum()
average_forecast = future["forecast_units"].mean()

col1, col2 = st.columns(2)
col1.metric("8-week Forecast", format_number(total_forecast))
col2.metric("Average Weekly Demand", format_number(average_forecast))

st.subheader("Forecast Table")
st.dataframe(
    future[["date", "forecast_horizon_week", "forecast_units", "forecast_lower", "forecast_upper"]],
    use_container_width=True,
    hide_index=True
)