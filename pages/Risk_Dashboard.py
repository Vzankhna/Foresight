import streamlit as st
import plotly.express as px
from src.app.helpers import(load_risk, page_header, require_data, format_rupees)

page_header(
    "Stock Risk Dashboard",
    "Stockout and overstock risk with recommended actions"
)
df = load_risk()
require_data(df, "Risk output is unavailable")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Reorder Now", int((df["recommended_action"] == "Reorder Now").sum()))
col2.metric("Markdown / Clear", int((df["recommended_action"] == "Markdown / Clear").sum()))
col3.metric("Watch / Volatile", int((df["recommended_action"] == "Watch / Volatile").sum()))
col4.metric("Healthy", int((df["recommended_action"] == "Healthy").sum()))
st.divider()

fig = px.scatter(
    df,
    x="stockout_risk_score",
    y="overstock_risk_score",
    size="sales_at_risk",
    color="recommended_action",
    hover_name="sku",
    hover_data=["category", "on_hand_units", "total_forecast_units", "sales_at_risk", "locked_capital"],
    title="Stockout vs Overstock Risk",
)
fig.add_vline(x=30, line_dash="dash")
fig.add_hline(y=30, line_dash="dash")
st.plotly_chart(fig, use_container_width=True)
st.subheader("Prioritised Actions")

priority = df[
    ["sku", "category", "risk_level", "recommended_action", "stockout_risk_score", "overstock_risk_score", "sales_at_risk", "locked_capital"]
].sort_values(
    ["risk_level", "sales_at_risk"],
    ascending=[True, False]
)

st.dataframe(
    priority,
    use_container_width=True,
    hide_index=True
)
st.subheader("Financial Exposure")

c1, c2 = st.columns(2)
c1.metric("Sales at Risk", format_rupees(df["sales_at_risk"].sum()))
c2.metric("Locked Capital", format_rupees(df["locked_capital"].sum()))