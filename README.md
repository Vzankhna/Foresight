## FORESIGHT Retail Demand Forecasting & Inventory Risk Intelligence Platform

FORESIGHT is a retail analytics platform that analyzes historical sales and inventory data, forecasts future product demand, identifies inventory risks and presents business insights through an interactive Streamlit dashboard.

## Features
- Sales and demand analysis
- Future demand forecasting
- Inventory health monitoring.
- Stockout and overstock risk detection.
- SKU/Product-level analysis.
- Interactive Streamlit dashboard.
- Executive summary and business insight.
- Automated data-processing pipeline.

## Tech Stack
- Python
- Pandas & NumPy
- Scikit-learn
- Streamlit
- Plotly / Charts
- CSV /JSON
- Joblib
- FastAPI/Uvicorn(When API service is enabled.)

## Project Structure

FORESIGHT/
|
├──data/
|    ├──raw/
|    ├──processed/
|
├──models/
|
├──outputs/
|
├──pages/
|    ├──Demand_Forecast.py
|    ├──Executive_Summary.py
|    ├──Inventory_Dashboard.py
|    ├──Product_Details.py
|    ├──Risk_Dashboard.py
|    ├──Sales_Analytics.py
|
├──scripts/
|    ├──run_pipeline.py
|
├──service/
|    ├──main.py
|
├──src/
|    ├──config.py
|    ├──forecast.py
|    ├──pipeline.py
|    ├──risk.py
|
├──utils/
|    ├──data_loader.py
|
├──app.py
|
├──REAFME.md

## Input Data
Place the followig files inside:

data/raw/
sales_daily.csv
sku_,aster.csv
calendar.csv
inventory_snapshots.csv

## Installation
Create and active a virtual environment:

python -m venv venv
## Windows:
venv\Scripts\activate

## install dependencies:
pip install -r requirements.txt

## Run Data Pipeline
From the FORESIGHT project root:
python scripts/run_pipeline.py

The pipeline generates processed datasets inside:
data/processed/

For examples:
analysis_ready_daily.csv
weekly_features.csv

## Run Dashboard:
Start the streamlit application:

streamlit run app.py

The browser will open FORESIGHT dashboard.

## Dashboard Pages:
1. Home/App:  Project overview and business KPIs
2. Demand Forecast: Future demand predictions
3. Executive Summary: Key insights and recommendations
4. Inventory Dashboard: Inventory health
5. Product Details: SKU-level analysis
6. Risk Dashboard: Stockout and overstock risks
7. Sales Analytics: Sales trends and performance.

## Project Workflow:
Raw Data
   ↓
EDA
   ↓
Feature Engineering
   ↓
Demand Forecasting
   ↓
Model Evaluation
   ↓
Risk Scoring
   ↓
Streamlit Dashboard
   ↓
Business Insights

## Project Goal
The goal of FORESIGHT is to providde a centralized retail intelligence platform that helps businesses understand demand, forecast future requirements, monitor inventory and identify potential inventory risks.