import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.app.helpers import (load_daily, load_forecast, load_risk, format_rupees, format_number)

st.set_page_config(
    page_title="FORESIGHT | Retail Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
  """
  <style>
    .stApp {
      background-color: #0b1120;
      color: #f8fafc;
    }

    .main .block-container {
      max-width: 1500px;
      padding-top: 2rem;
      padding-bottom: 3rem;
      padding-left: 2rem;
      padding-right: 2rem;
    }

    #MainMenu {
      visibility: hidden;
    }

    footer {
      visibility: hidden;
    }

    header {
      visibility: hidden;
    }

    [data-testid="stSidebar"] {
      background-color: #080d19;
      border-right: 1px solid #1e293b;
    }

    [data-testid="stSidebar"] * {
      color: #e5e7eb;
    }

    h1, h2, h3, h4, h5, h6 {
      color: #f8fafc !important;
    }

    p {
      color: #cbd5e1;
    }

    .stCaption {
      color: #94a3b8 !important;
    }

    [data-testid="stMetric"] {
      background-color: #111827;
      border: 1px solid #1f2937;
      border-radius: 16px;
      padding: 20px;
      min-height: 125px;
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
    }

    [data-testid="stMetricLabel"] {
      color: #94a3b8 !important;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }

    [data-testid="stMetricValue"] {
      color: #f8fafc !important;
      font-size: 1.75rem;
      font-weight: 800;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
      background-color: #111827;
      border: 1px solid #1f2937;
      border-radius: 16px;
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.20);
    }

    hr {
      border-color: #1e293b !important;
    }

    .section-gap {
      height: 22px;
    }

    .js-plotly-plot .plotly .modebar {
      display: none !important;
    }

  </style>
  """,
  unsafe_allow_html=True,
)

daily = load_daily()
forecast = load_forecast()
risk = load_risk()

if daily is None or daily.empty:
    st.error("Processed sales data is not available.")
    st.info("Please run the FORESIGHT data pipeline before opening the dashboard.")
    st.stop()

if forecast is None:
    forecast = pd.DataFrame()

if risk is None:
    risk = pd.DataFrame()

daily = daily.copy()
forecast = forecast.copy()
risk = risk.copy()

if "date" in daily.columns:
    daily["date"] = pd.to_datetime(
        daily["date"],
        errors="coerce"
    )
    daily = daily.dropna(subset=["date"])

if "date" in forecast.columns:
    forecast["date"] = pd.to_datetime(
        forecast["date"],
        errors="coerce"
    )

total_revenue = (
    daily["revenue"].sum()
    if "revenue" in daily.columns
    else 0
)
total_units = (
    daily["units_sold"].sum()
    if "units_sold" in daily.columns
    else 0
)
active_skus = (
    daily["sku"].nunique()
    if "sku" in daily.columns
    else 0
)
sales_at_risk = (
    risk["sales_at_risk"].sum()
    if not risk.empty and "sales_at_risk" in risk.columns
    else 0
)
locked_capital = (
    risk["locked_capital"].sum()
    if not risk.empty and "locked_capital" in risk.columns
    else 0
)
risk_skus = (
    risk["sku"].nunique()
    if not risk.empty and "sku" in risk.columns
    else 0
)
forecast_records = len(forecast)
forecast_skus = (
    forecast["sku"].nunique()
    if not forecast.empty and "sku" in forecast.columns
    else 0
)
forecast_periods = (
    forecast["date"].nunique()
    if not forecast.empty and "date" in forecast.columns
    else 0
)
average_daily_revenue = (
    daily["revenue"].mean()
    if "revenue" in daily.columns and not daily.empty
    else 0
)
average_daily_units = (
    daily["units_sold"].mean()
    if "units_sold" in daily.columns and not daily.empty
    else 0
)

if "date" in daily.columns and not daily.empty:
    data_start = daily["date"].min()
    data_end = daily["date"].max()
    data_days = (data_end - data_start).days + 1
else:
    data_start = None
    data_end = None
    data_days = 0

high_risk_count = 0
medium_risk_count = 0
low_risk_count = 0

if not risk.empty:
    possible_risk_columns = ["risk_level", "risk_category", "risk", "severity"]
    risk_column = None
    for column in possible_risk_columns:
        if column in risk.columns:
            risk_column = column
            break
        
    if risk_column:
        risk_values = (
            risk[risk_column]
            .astype(str)
            .str.lower()
        )
        high_risk_count = (
            risk_values
            .str.contains("high")
            .sum()
        )
        medium_risk_count = (
            risk_values
            .str.contains("medium")
            .sum()
        )
        low_risk_count = (
            risk_values
            .str.contains("low")
            .sum()
        )
st.title("FORESIGHT")
st.subheader("Retail Demand & Inventory Intelligence")
st.write(
    "A centralized intelligence layer for monitoring sales performance, "
    "customer demand, product movement, inventory exposure and future demand."
)
st.divider()
st.subheader("Executive Overview")
st.caption("High-level business indicators generated from the latest processed retail data.")

k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    st.metric("TOTAL REVENUE", format_rupees(total_revenue))
with k2:
    st.metric("UNITS SOLD", format_number(total_units))
with k3:
    st.metric("ACTIVE SKUs", format_number(active_skus))
with k4:
    st.metric("SALES AT RISK", format_rupees(sales_at_risk))

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)
st.subheader("Business Health")
st.caption("Operational indicators showing inventory exposure and business activity.")

h1, h2, h3, h4 = st.columns(4, gap="medium")
with h1:
    with st.container(border=True):
        st.metric("REVENUE AT RISK", format_rupees(sales_at_risk))
        st.caption("Estimated sales exposure associated with inventory risk.")

with h2:
    with st.container(border=True):
        st.metric("LOCKED CAPITAL", format_rupees(locked_capital))
        st.caption("Capital currently associated with inventory exposure.")

with h3:
    with st.container(border=True):
        st.metric("RISK SKUs", format_number(risk_skus))
        st.caption("Products currently identified by the risk engine.")

with h4:
    with st.container(border=True):
        st.metric("AVG DAILY REVENUE", format_rupees(average_daily_revenue))
        st.caption("Average revenue generated per available sales day.")

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)

st.subheader("Sales Performance")
st.caption("Historical sales movement across revenue and unit volume.")
sales_left, sales_right = st.columns([1.25, 1], gap="large")

with sales_left:
    with st.container(border=True):
        st.subheader("Revenue Trend")
        st.caption("Daily revenue movement over the available historical period.")

        if ("date" in daily.columns and "revenue" in daily.columns):
            revenue_trend = (
                daily
                .groupby("date", as_index=False)["revenue"]
                .sum()
                .sort_values("date")
            )
            fig_revenue = go.Figure()
            fig_revenue.add_trace(
                go.Scatter(
                    x=revenue_trend["date"],
                    y=revenue_trend["revenue"],
                    mode="lines",
                    fill="tozeroy",
                    line=dict(color="#38bdf8",width=3),
                    fillcolor="rgba(56,189,248,0.10)",
                    hovertemplate=(
                        "<b>%{x|%d %b %Y}</b>"
                        "<br>Revenue: ₹%{y:,.0f}"
                        "<extra></extra>"
                    )
                )
            )
            fig_revenue.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                showlegend=False,
                hovermode="x unified",
                font=dict(color="#cbd5e1"),
                xaxis=dict(title=None, showgrid=False, color="#94a3b8"),
                yaxis=dict(title="Revenue", tickformat=",.0f", gridcolor="#1f2937", color="#94a3b8")
            )
            st.plotly_chart(
                fig_revenue,
                use_container_width=True,
                config={"displayModeBar": False}
            )
        else:
            st.info("Revenue data is not available.")

with sales_right:
    with st.container(border=True):
        st.subheader("Units Sold Trend")
        st.caption("Daily product volume across the historical sales period.")

        if ("date" in daily.columns and "units_sold" in daily.columns):
            unit_trend = (
                daily
                .groupby("date",as_index=False)["units_sold"]
                .sum()
                .sort_values("date")
            )
            fig_units = go.Figure()
            fig_units.add_trace(
                go.Scatter(
                    x=unit_trend["date"],
                    y=unit_trend["units_sold"],
                    mode="lines",
                    fill="tozeroy",
                    line=dict(color="#a78bfa",width=3),
                    fillcolor="rgba(167,139,250,0.10)",
                    hovertemplate=(
                        "<b>%{x|%d %b %Y}</b>"
                        "<br>Units: %{y:,.0f}"
                        "<extra></extra>"
                    )
                )
            )
            fig_units.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                showlegend=False,
                hovermode="x unified",
                font=dict(color="#cbd5e1"),
                xaxis=dict(title=None, showgrid=False, color="#94a3b8"),
                yaxis=dict(title="Units", gridcolor="#1f2937", color="#94a3b8")
            )
            st.plotly_chart(
                fig_units,
                use_container_width=True,
                config={"displayModeBar": False}
            )
        else:
            st.info("Unit sales data is not available.")
st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)
st.subheader("Inventory Intelligence")
st.caption( "Inventory actions and risk exposure identified by the intelligence engine.")
inv_left, inv_right = st.columns([1.15, 1], gap="large")

with inv_left:
    with st.container(border=True):
        st.subheader("Inventory Action Distribution")
        st.caption("Recommended operational actions across risk-identified products.")

        if (not risk.empty and "recommended_action" in risk.columns):
            action_counts = (
                risk["recommended_action"]
                .fillna("No Action")
                .value_counts()
                .reset_index()
            )
            action_counts.columns = ["Action","SKU Count"]
            fig_action = px.bar(
                action_counts,
                x="Action",
                y="SKU Count",
                text="SKU Count"
            )
            fig_action.update_traces(
                marker_color="#38bdf8",
                textposition="outside",
                textfont=dict(color="#f8fafc")
            )
            fig_action.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                showlegend=False,
                font=dict(color="#cbd5e1"),
                xaxis=dict(title=None,showgrid=False,color="#94a3b8"),
                yaxis=dict(title="SKU Count", gridcolor="#1f2937", color="#94a3b8")
            )
            st.plotly_chart(fig_action, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Inventory action data is not available.")

with inv_right:
    with st.container(border=True):
        st.subheader("Risk Overview")
        st.caption("Distribution of identified inventory risk levels.")

        if (high_risk_count + medium_risk_count + low_risk_count) > 0:
            risk_df = pd.DataFrame(
                {
                    "Risk Level": ["High Risk", "Medium Risk", "Low Risk"],
                    "SKU Count": [high_risk_count, medium_risk_count, low_risk_count]
                }
            )
            fig_risk = px.bar(risk_df, x="Risk Level", y="SKU Count", text="SKU Count")
            fig_risk.update_traces(marker_color="#8b5cf6", textposition="outside")
            fig_risk.update_layout(height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                showlegend=False,
                font=dict(color="#cbd5e1"),
                xaxis=dict(title=None, showgrid=False, color="#94a3b8"),
                yaxis=dict(title="SKUs", gridcolor="#1f2937", color="#94a3b8")
            )
            st.plotly_chart(fig_risk, use_container_width=True,config={"displayModeBar": False})
        else:
            st.info("Risk-level information is not available.")

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)
st.subheader("Forecast Intelligence")
st.caption("Coverage and size of the generated demand forecasting dataset.")

f1, f2, f3, f4 = st.columns(4,gap="medium")

with f1:
    st.metric("FORECAST RECORDS", format_number(forecast_records))
with f2:
    st.metric("FORECAST SKUs",format_number(forecast_skus))
with f3:
    st.metric("FORECAST PERIODS",format_number(forecast_periods))
with f4:
    st.metric("AVG DAILY UNITS",format_number(average_daily_units))

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)
st.subheader("Top Products")
st.caption("Highest-performing products based on available sales history.")

if ("sku" in daily.columns and "revenue" in daily.columns):
    product_summary = (daily
        .groupby("sku", as_index=False)
        .agg(Revenue=("revenue", "sum"),
            Units=("units_sold","sum"
            ) if "units_sold" in daily.columns else (
                "revenue",
                "count")
        )
        .sort_values("Revenue",ascending=False)
        .head(10)
    )
    product_summary["Revenue"] = ( product_summary["Revenue"].round(0))
    st.dataframe(product_summary, use_container_width=True, hide_index=True)
else:
    st.info("Product-level sales information is not available.")

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)
st.subheader("Data Coverage")
st.caption("Scope of the data currently powering FORESIGHT.")
d1, d2, d3, d4 = st.columns(4,gap="medium")

with d1:
    with st.container(border=True):
        st.metric("SALES DAYS", format_number(data_days))
        if data_start is not None:
            st.caption(f"{data_start:%d %b %Y} → {data_end:%d %b %Y}")
        else:
            st.caption("Date coverage unavailable")

with d2:
    with st.container(border=True):
        st.metric("SALES RECORDS", format_number(len(daily)))
        st.caption("Processed daily sales observations")

with d3:
    with st.container(border=True):
        st.metric("PRODUCT COVERAGE", format_number(active_skus))
        st.caption("Unique products represented")

with d4:
    with st.container(border=True):
        st.metric("RISK COVERAGE",format_number(risk_skus))
        st.caption("Products evaluated by risk engine")

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)

st.subheader("Executive Takeaways")
st.caption("Automatically generated observations from the current dashboard data.")
takeaway_col1, takeaway_col2 = st.columns(2,gap="medium")

with takeaway_col1:
    with st.container(border=True):
        st.markdown("### Sales")
        if total_revenue > 0:
            st.write(
                f"Total recorded revenue is "
                f"**{format_rupees(total_revenue)}** "
                f"across **{format_number(data_days)}** sales days."
            )
            st.write(
                f"Average daily revenue is "
                f"**{format_rupees(average_daily_revenue)}**."
            )
        else:
            st.write("Revenue information is currently unavailable.")

with takeaway_col2:
    with st.container(border=True):
        st.markdown("### Inventory")
        if risk_skus > 0:
            st.write(
                f"The risk engine has identified "
                f"**{format_number(risk_skus)} SKUs** "
                f"requiring inventory attention."
            )
            st.write(
                f"Current sales exposure is "
                f"**{format_rupees(sales_at_risk)}**."
            )
        else:
            st.write("No inventory risk records are currently available.")

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)
st.subheader("FORESIGHT Intelligence Workflow")
st.caption("End-to-end journey from raw retail data to business recommendations.")

workflow = [
    ("01", "Data Foundation", "Sales, product, calendar and inventory data."),
    ("02", "Exploratory Analysis", "Trends, patterns, relationships and data quality."),
    ("03", "Demand Baseline", "Historical demand and baseline calculations."),
    ("04", "Forecasting", "Future demand estimation using forecasting models."),
    ("05", "Risk Scoring", "Inventory exposure and product-level risk identification."),
    ("06", "Intelligence Dashboard", "Interactive monitoring of business performance."),
    ("07", "Deployment", "Production-ready retail intelligence platform."),
    ("08", "Executive Readout",  "Insights and recommendations for business decisions.")
]

for row_start in range(0, len(workflow), 4):
    row = workflow[
        row_start:
        row_start + 4
    ]
    columns = st.columns(4, gap="medium")

    for column, item in zip(columns, row):
        number, title, description = item

        with column:
            with st.container(border=True):
                st.markdown(f"### {number}")
                st.markdown(f"**{title}**")
                st.caption(description)

st.markdown(
    "<div class='section-gap'></div>",
    unsafe_allow_html=True
)
with st.container(border=True):
    st.subheader("Explore FORESIGHT")
    st.write(
        "Use the sidebar to explore detailed Sales Performance, "
        "Customer Demand, Product Performance, Inventory Health, "
        "Stock Risk, Promotion Analysis, Seasonality, Forecasting "
        "and Executive Recommendations."
    )
st.divider()
st.caption("FORESIGHT · Retail Demand & Inventory Intelligence")