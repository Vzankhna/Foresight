import streamlit as st
import plotly.express as px
from src.app.helpers import(load_daily, sidebar_filters, page_header, require_data, format_rupees, format_number)

page_header(
    "Sales Analytics",
    "Historical revenue, units and promotion performance"
)
df = load_daily()
require_data(df, "Sales data is unavailable. Run the pipeline first")
df = sidebar_filters(df)

col1, col2, col3 = st.columns(3)
col1.metric(
    "Revenue",
    format_rupees(df["revenue"].sum())
)
col2.metric(
    "Units",
    df["units_sold"].sum()
)
col3.metric(
    "Average Price",
    format_rupees(df["unit_price"].mean())
)
st.divider()

daily_sales = (
    df.groupby("date")
    .agg(
        revenue=("revenue", "sum"),
        units=("units_sold", "sum")
    )
    .reset_index()
)
fig = px.line(
    daily_sales,
    x="date",
    y="revenue",
    title="Daily Revenue"
)
st.plotly_chart(
    fig,
    use_container_width=True
)
category_sales = (
    df.groupby("category")
    .agg(
        revenue=("revenue", "sum"),
        units=("units_sold", "sum")
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)
fig2 = px.bar(
    category_sales,
    x="category",
    y="revenue",
    title="Revenue by Category"
)
st.plotly_chart(
    fig2,
    use_container_width=True
)
promo = (
    df.groupby("promo_flag")
    .agg(
        revenue=("revenue", "sum"),
        units=("units_sold", "sum")
    )
    .reset_index()
)
promo["promo_flag"] = promo["promo_flag"].map({
    0: "No Promotion",
    1: "Promotion"
})
fig3 = px.bar(
    promo,
    x="promo_flag",
    y="units",
    title="Units Sold: Promotion vs Non-Promotion"
)
st.plotly_chart(
    fig3,
    use_container_width=True
)