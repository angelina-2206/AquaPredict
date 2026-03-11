import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface KPIData {
  current_reservoir_level_pct: number;
  current_reservoir_level: number;
  capacity: number;
  forecasted_demand: number;
  avg_monthly_demand: number;
  avg_monthly_inflow: number;
  risk_indicator: 'Safe' | 'Moderate' | 'High' | 'Critical' | string;
  metrics: {
    RMSE: number;
    MAE: number;
  };
}

export interface DemandData {
  month: string;
  actual: number | null;
  forecast: number;
  lower: number;
  upper: number;
}

export interface StorageData {
  month: string;
  storage: number;
  capacity: number;
  threshold: number;
}

export interface RainfallData {
  month: string;
  rainfall: number;
  inflow: number;
}

export interface SupplyDemandData {
  month: string;
  supply: number;
  demand: number;
  gap: number;
}

export interface AnalysisResponse {
  kpis: KPIData;
  charts: {
    demandForecast: DemandData[];
    reservoirStorage: StorageData[];
    rainfall: RainfallData[];
    supplyDemand: SupplyDemandData[];
  };
}

export const fetchStates = async (): Promise<string[]> => {
  const { data } = await apiClient.get('/states');
  return data.states;
};

export const fetchAnalysis = async (
  state: string,
  forecastMonths: number = 12,
  rainfallVariation: number = 0.0
): Promise<AnalysisResponse> => {
  const { data } = await apiClient.get(`/analysis/${encodeURIComponent(state)}`, {
    params: {
      forecast_months: forecastMonths,
      rainfall_variation: rainfallVariation,
    },
  });
  return data;
};
