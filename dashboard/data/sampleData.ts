// Sample data for AquaPredict dashboard

export const monthLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export const demandForecastData = monthLabels.map((month, i) => ({
  month,
  actual: [42, 38, 45, 52, 61, 68, 74, 72, 63, 55, 47, 43][i],
  forecast: [44, 40, 47, 54, 63, 70, 76, 73, 64, 56, 48, 44][i],
  lower: [40, 36, 43, 50, 59, 66, 72, 69, 60, 52, 44, 40][i],
  upper: [48, 44, 51, 58, 67, 74, 80, 77, 68, 60, 52, 48][i],
}));

export const reservoirStorageData = monthLabels.map((month, i) => ({
  month,
  storage: [78, 72, 65, 58, 50, 44, 40, 42, 48, 56, 65, 74][i],
  capacity: 100,
  threshold: 30,
}));

export const rainfallData = monthLabels.map((month, i) => ({
  month,
  rainfall: [85, 60, 45, 30, 15, 8, 5, 12, 35, 55, 75, 90][i],
  inflow: [70, 50, 38, 25, 12, 6, 4, 10, 28, 45, 62, 78][i],
}));

export const supplyDemandData = monthLabels.map((month, i) => ({
  month,
  supply: [65, 58, 52, 45, 38, 32, 28, 30, 36, 44, 54, 62][i],
  demand: [42, 38, 45, 52, 61, 68, 74, 72, 63, 55, 47, 43][i],
  gap: [65, 58, 52, 45, 38, 32, 28, 30, 36, 44, 54, 62][i] - [42, 38, 45, 52, 61, 68, 74, 72, 63, 55, 47, 43][i],
}));

export const riskLevel = (gap: number): "Low" | "Moderate" | "High" => {
  if (gap > 10) return "Low";
  if (gap > 0) return "Moderate";
  return "High";
};
