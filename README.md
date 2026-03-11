# AquaPredict: Full-Stack Water Intelligence Platform

## 🌊 Project Overview

AquaPredict is a comprehensive, full-stack software system designed for sustainable water resource management. It provides powerful predictive analytics, water demand forecasting, and reservoir storage simulations. Originally built as a Streamlit prototype, **AquaPredict is now a modern web application** featuring a high-performance Python FastAPI backend and a dynamic, responsive React frontend.

## 🚀 Key Features

- **📊 Time Series Forecasting**: ARIMA-based water demand prediction models trained on historical data.
- **💧 Reservoir Simulation**: Physical water balance modeling capturing storage dynamics under various pressure scenarios.
- **⚖️ Gap Analysis**: Supply-demand comparison alerting to potential shortage windows and establishing risk classifications.
- **🌍 Interactive Dashboards**: A state-of-the-art React frontend utilizing Recharts and dynamic SVG mapping for data exploration.
- **🔄 Global State Sync**: Select any Indian state (e.g., Andhra Pradesh, Telangana, Maharashtra) to instantly re-calculate and re-render the entire analytical pipeline for that region.

## 💻 Tech Stack

### Frontend (User Interface)
- **Framework**: React 18, Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS, generic UI components (Radix UI)
- **Data Fetching**: React Query (`@tanstack/react-query`), Axios
- **Data Visualization**: Recharts (Area, Line, Bar charts)
- **Icons**: Lucide React

### Backend (Analytical Engine & API)
- **Framework**: FastAPI, Uvicorn
- **Language**: Python 3.10+
- **Data Science / Modeling**: Pandas, NumPy, Statsmodels (ARIMA)
- **Architecture**: RESTful API endpoints serving JSON payloads.

---

## 📁 Project Structure

AquaPredict utilizes a **monorepo** architecture, housing both the Python backend and React frontend within the same repository.

```text
AquaPredict/
├── api.py                  # Main FastAPI Application Entrypoint
├── data/                   # Datasets (e.g., master_reservoir_dataset.csv)
├── preprocessing/          # Python: Data ingestion and cleaning modules
├── forecasting/            # Python: ARIMA demand forecasting engine & React: DemandForecast.tsx
├── simulation/             # Python: Reservoir modeling & React: ReservoirSimulation.tsx
├── analysis/               # Python: Gap analysis & React: SupplyDemandAnalysis.tsx, RainfallInflow.tsx
├── dashboard/              # React: Main UI components, layout, App.tsx, main.tsx, StateContext
├── public/                 # Static assets (favicon)
├── index.html              # Vite React entry HTML
├── package.json            # Node.js dependencies
├── vite.config.ts          # Vite build configuration
├── tailwind.config.ts      # Tailwind CSS configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🛠️ Installation & Setup

You will need both **Python** and **Node.js** installed on your system.

### 1. Backend Setup (Python)
Navigate to the root directory and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Frontend Setup (Node.js)
In the same root directory, install the Node packages:
```bash
npm install
```

---

## ▶️ Running the Application

To run the full application locally, you need to spin up both the FastAPI server and the Vite React server simultaneously in two separate terminal windows.

### Terminal 1: Start the Backend (FastAPI)
Run the Python API on `localhost:8000`:
```bash
python -m uvicorn api:fastapi_app --reload
```
*The API will boot, load the data preprocessors, and wait for frontend queries.*

### Terminal 2: Start the Frontend (Vite)
Run the React Dashboard:
```bash
npm run dev
```
*Vite will start the dev server, usually at `http://localhost:8080/` or `http://localhost:5173/`.*

Open the local network link provided by Vite in your browser to interact with AquaPredict!

---

## ⚙️ How It Works (Data Flow)

1. **User Interaction**: The user selects a state (e.g., "Maharashtra") from the global `StateContext` dropdown in the React top bar.
2. **React Query**: `axios` intercepts the state change and fires a `GET` request to `http://localhost:8000/api/analysis/Maharashtra`.
3. **FastAPI Processing**: 
   - Python receives the request.
   - It filters the `aquapredict_master_reservoir_dataset.csv` via the `DataPreprocessor`.
   - The data is routed through the ARIMA forecasting and Reservoir Simulation modules.
   - A compiled analytical response containing KPIs and chart axes is constructed.
4. **Data Visualization**: React receives the structured JSON from Python and smoothly re-renders the Recharts visualizations on the dashboard.

## 🎯 Risk Classification
The analytical engine categorizes periods into:
- **🟢 Safe**: Storage > 60% capacity
- **🟠 Moderate**: Storage 30-60% capacity (Stress Zone)
- **🔴 Critical**: Storage < 30% capacity (Immediate Action Needed)

---
*Developed for evidence-based water resource management and policy planning.*