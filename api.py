import sys
import unittest.mock as mock

# Mock streamlit to bypass any streamlit errors when running outside of Streamlit
mock_st = mock.MagicMock()
sys.modules['streamlit'] = mock_st

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import pandas as pd
import numpy as np

# Import the AquaPredict app which contains the logic
from app import AquaPredictApp

# Initialize FastAPI app
fastapi_app = FastAPI(title="AquaPredict API")

# Add CORS middleware to allow the React frontend to communicate with this backend
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instance of AquaPredictApp
aqua_app = None

@fastapi_app.on_event("startup")
async def startup_event():
    global aqua_app
    aqua_app = AquaPredictApp()
    # Load and process data once on startup
    success = aqua_app.load_and_process_data()
    if not success:
        print("Failed to load AquaPredict data.")

@fastapi_app.get("/api/states")
def get_states():
    if aqua_app.master_data is None:
        return {"states": []}
    states = aqua_app.preprocessor.get_states(aqua_app.master_data)
    return {"states": states}

@fastapi_app.get("/api/analysis/{state}")
def get_analysis_for_state(state: str, forecast_months: int = 12, rainfall_variation: float = 0.0):
    """
    Run the AquaPredict pipeline for a given state and return formatted data
    suitable for the React dashboard charts.
    """
    if aqua_app.master_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # Filter data for selected state
    state_data = aqua_app.preprocessor.get_state_data(aqua_app.master_data, state)
    
    # Temporarily set master_data for the app instance to just this state's data 
    # so the app methods use it correctly
    original_master_data = aqua_app.master_data
    aqua_app.master_data = state_data
    
    try:
        # Run forecast
        forecast_results, metrics = aqua_app.run_forecast(forecast_months)
        if forecast_results is None:
            raise HTTPException(status_code=500, detail="Forecast failed")
            
        # Run simulation
        simulation_results = aqua_app.run_simulation(forecast_results, rainfall_variation)
        if simulation_results is None:
            raise HTTPException(status_code=500, detail="Simulation failed")
            
        # Run gap analysis
        gap_results = aqua_app.run_gap_analysis(simulation_results, forecast_results)
        
        # Prepare Chart Data
        # Demand Forecast Data
        demand_data = []
        for i, row in forecast_results.iterrows():
            month_str = row['date'].strftime('%b')
            demand_data.append({
                "month": month_str,
                "actual": None, # Forecast typically doesn't have actuals for future
                "forecast": round(row['forecast'], 1),
                "lower": round(row.get('lower_ci', row['forecast'] * 0.9), 1),
                "upper": round(row.get('upper_ci', row['forecast'] * 1.1), 1)
            })
            
        # Reservoir Storage Data
        storage_data = []
        for i, row in simulation_results.iterrows():
            storage_data.append({
                "month": row['date'].strftime('%b'),
                "storage": round(row['storage_level'], 1),
                "capacity": aqua_app.simulator.storage_capacity,
                "threshold": aqua_app.simulator.storage_capacity * 0.3 # 30% threshold
            })
            
        # Rainfall Data (we use historical trailing data for this usually)
        recent_data = state_data.tail(12)
        rainfall_data = []
        for i, row in recent_data.iterrows():
            rainfall_data.append({
                "month": row['date'].strftime('%b'),
                "rainfall": round(row['rainfall'], 1),
                "inflow": round(row['inflow'], 1)
            })
            
        # Supply Demand Gap Data
        supply_demand_data = []
        if gap_results is not None:
             for i, row in gap_results.iterrows():
                 supply_demand_data.append({
                     "month": row['date'].strftime('%b'),
                     "supply": round(row['supply'], 1),
                     "demand": round(row['demand'], 1),
                     "gap": round(row['gap'], 1)
                 })
                 
        # Overview KPIs
        last_storage = simulation_results['storage_level'].iloc[-1]
        capacity = aqua_app.simulator.storage_capacity
        storage_pct = (last_storage / capacity) * 100
        total_demand = forecast_results['forecast'].sum()
        risk = simulation_results['risk_status'].iloc[-1]
        
        kpis = {
            "current_reservoir_level_pct": round(storage_pct, 1),
            "current_reservoir_level": round(last_storage, 1),
            "capacity": capacity,
            "forecasted_demand": round(total_demand, 1),
            "avg_monthly_demand": round(total_demand / len(forecast_results), 1),
            "avg_monthly_inflow": round(recent_data['inflow'].mean(), 1),
            "risk_indicator": risk,
            "metrics": {
                "RMSE": round(metrics.get("RMSE", 0), 2) if metrics else 0,
                "MAE": round(metrics.get("MAE", 0), 2) if metrics else 0
            }
        }
        
    finally:
        # Restore original master data
        aqua_app.master_data = original_master_data
        
    return {
        "kpis": kpis,
        "charts": {
            "demandForecast": demand_data,
            "reservoirStorage": storage_data,
            "rainfall": rainfall_data,
            "supplyDemand": supply_demand_data
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:fastapi_app", host="0.0.0.0", port=8000, reload=True)
