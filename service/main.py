import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config import FORECAST_FILE, RISK_FILE

app = FastAPI(
    title="FORESIGHT Scoring API",
    description="Demand forecast and inventory risk service",
    version="1.0.0"
)

class SKURequest(BaseModel):
    sku: str

@app.get("/")
def health():
    return {
        "status": "healthy",
        "message": "FORESIGHT API is running"
    }

@app.get("/skus")
def list_skus():
    if not FORECAST_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Forecast file not found"
        )

    forecast = pd.read_csv(FORECAST_FILE)

    if "sku" not in forecast.columns:
        raise HTTPException(
            status_code=500,
            detail="SKU column not found in forecast file"
        )

    return {
        "skus": sorted(
            forecast["sku"].dropna().unique().tolist()
        )
    }

@app.post("/predict")
def predict(request: SKURequest):
    sku = request.sku.strip()

    if not sku:
        raise HTTPException(
            status_code=400,
            detail="SKU cannot be empty."
        )

    if not FORECAST_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Forecast file not found."
        )

    if not RISK_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Risk file not found."
        )

    forecast = pd.read_csv(FORECAST_FILE)
    risk = pd.read_csv(RISK_FILE)

    sku_forecast = forecast[forecast["sku"] == sku]
    sku_risk = risk[risk["sku"] == sku]

    if sku_forecast.empty:
        raise HTTPException(
            status_code=404,
            detail=f"SKU {sku} not found"
        )

    forecast_records = sku_forecast[
        [
            "date",
            "forecast_horizon_week",
            "forecast_units",
            "forecast_lower",
            "forecast_upper"
        ]
    ].to_dict(orient="records")

    risk_record = (
        sku_risk.iloc[0].to_dict()
        if not sku_risk.empty
        else {}
    )

    return {
        "sku": sku,
        "forecast": forecast_records,
        "risk": risk_record
    }