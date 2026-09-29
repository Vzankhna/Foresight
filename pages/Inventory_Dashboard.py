import streamlit as st
import plotly.express as px
from src.app.helpers import(load_risk, sidebar_filters, page_header, require_data, format_rupees, format_number)

page_header(
    "Inventory Dashboard",
    "Current stock, on-order inventory and capital exposure"
)
df = load_risk()
require_data(
    df,
    "Risk data is unavailable. Run risk scoring first."
)
df = sidebar_filters(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("On Hand", format_number(df["on_hand_units"].sum()))
col2.metric("On Order", format_number(df["on_order_units"].sum()))
col3.metric("Inventory Capital", format_rupees(df["locked_capital"].sum()))
col4.metric("Reorder Candidates", str((df["recommended_action"] == "Reorder Now").sum()))
st.divider()

category_inventory = (
    df.groupby("category")
    .agg(
        on_hand=("on_hand_units", "sum"),
        on_order=("on_order_units", "sum"),
        locked_capital=("locked_capital", "sum")
    )
    .reset_index()
)
fig = px.bar(
    category_inventory,
    x="category",
    y=["on_hand", "on_order"],
    barmode="group",
    title="Inventory by Category"
)
st.plotly_chart(
    fig,
    use_container_width=True
)
st.subheader("Inventory Position")
st.dataframe(
    df[["sku", "category", "on_hand_units", "on_order_units", "average_weekly_demand", "lead_time_days", "reorder_point"]]
    .sort_values("on_hand_units"),
    use_container_width=True,
    hide_index=True
)