import streamlit as st
import plotly.express as px
from src.app.helpers import(load_daily, load_weekly, load_forecast, load_risk, page_header, require_data, format_rupees)

page_header(
    "Product Details",
    "SKU-level product, demand and incentory analysis"
)
daily = load_daily()
weekly = load_weekly()
risk = load_risk()
forecast = load_forecast()

require_data(daily, "Daily data is unavailable")
sku_list = sorted(daily["sku"].unique().tolist())
sku = st.selectbox("Select Product", sku_list)
product = daily[daily["sku"] == sku]
risk_row = risk[risk["sku"] == sku]
future = forecast[forecast["sku"] == sku]
latest = product.sort_values("date").iloc[-1]
st.subheader(f"{sku} —— {latest['product_name']}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Category", latest["category"])
col2.metric("Subcategory", latest["subcategory"])
col3.metric("Revenue", format_rupees(product["revenue"].sum()))
col4.metric("Units Sold", f"{product['units_sold'].sum():,.0f}")
st.divider()

history = (weekly[weekly["sku"] == sku].sort_values("date").tail(52))
fig = px.line(history, x="date", y="units_sold", title="Weekly Demand History")
st.plotly_chart(fig, use_container_width=True)

if not future.empty:
    fig2 = px.line(
        future,
        x="date",
        y="forecast_units",
        title="Forecast"
    )
    st.plotly_chart(fig2, use_container_width=True)

if not risk_row.empty:
    row = risk_row.iloc[0]
    st.subheader("Risk Assessment")

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Level", row["risk_level"])
    c2.metric("Recommended Action", row["recommended_action"])
    c3.metric("Sales at Risk", format_rupees(row["sales_at_risk"]))

    st.write("Stockout Risk Score:", f"{row['stockout_risk_score']:.1f}")
    st.write("Overstock Risk Score:", f"{row['overstock_risk_score']:.1f}")
    st.write("Current Stock:", f"{row['on_hand_units']:,.0f}")
    st.write("On Order:", f"{row['on_order_units']:,.0f}")