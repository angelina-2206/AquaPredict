// Indian states and reservoir data for AquaPredict

export const indianStates = [
  { value: "andhra-pradesh", label: "Andhra Pradesh" },
  { value: "telangana", label: "Telangana" },
  { value: "rajasthan", label: "Rajasthan" },
  { value: "maharashtra", label: "Maharashtra" },
  { value: "karnataka", label: "Karnataka" },
  { value: "tamil-nadu", label: "Tamil Nadu" },
  { value: "gujarat", label: "Gujarat" },
  { value: "madhya-pradesh", label: "Madhya Pradesh" },
  { value: "kerala", label: "Kerala" },
] as const;

export type Season = "winter" | "summer" | "monsoon" | "post-monsoon";

export const seasons: { value: Season; label: string; months: string }[] = [
  { value: "winter", label: "Winter (Dec–Feb)", months: "Dec–Feb" },
  { value: "summer", label: "Summer (Mar–May)", months: "Mar–May" },
  { value: "monsoon", label: "Monsoon (Jun–Sep)", months: "Jun–Sep" },
  { value: "post-monsoon", label: "Post-Monsoon (Oct–Nov)", months: "Oct–Nov" },
];

export interface ReservoirInfo {
  name: string;
  state: string;
  x: number; // % position on map
  y: number;
  capacity: number; // in MCM
  levels: Record<Season, number>; // % filled per season
}

export const reservoirs: ReservoirInfo[] = [
  // Andhra Pradesh — SE India
  { name: "Nagarjuna Sagar", state: "Andhra Pradesh", x: 54, y: 62, capacity: 11472, levels: { winter: 62, summer: 35, monsoon: 88, "post-monsoon": 72 } },
  { name: "Srisailam", state: "Andhra Pradesh", x: 50, y: 60, capacity: 8722, levels: { winter: 58, summer: 30, monsoon: 85, "post-monsoon": 68 } },
  // Telangana — central-south
  { name: "Jurala", state: "Telangana", x: 49, y: 57, capacity: 895, levels: { winter: 55, summer: 28, monsoon: 82, "post-monsoon": 65 } },
  { name: "Singur", state: "Telangana", x: 52, y: 55, capacity: 854, levels: { winter: 50, summer: 22, monsoon: 78, "post-monsoon": 60 } },
  // Rajasthan — NW India
  { name: "Rana Pratap Sagar", state: "Rajasthan", x: 33, y: 30, capacity: 2910, levels: { winter: 45, summer: 18, monsoon: 72, "post-monsoon": 55 } },
  { name: "Jawai Dam", state: "Rajasthan", x: 30, y: 33, capacity: 514, levels: { winter: 40, summer: 12, monsoon: 65, "post-monsoon": 48 } },
  // Maharashtra — west-central
  { name: "Koyna", state: "Maharashtra", x: 36, y: 55, capacity: 2797, levels: { winter: 70, summer: 40, monsoon: 95, "post-monsoon": 80 } },
  { name: "Jayakwadi", state: "Maharashtra", x: 42, y: 50, capacity: 2909, levels: { winter: 52, summer: 25, monsoon: 80, "post-monsoon": 62 } },
  // Karnataka — south-central
  { name: "Tungabhadra", state: "Karnataka", x: 42, y: 64, capacity: 3725, levels: { winter: 60, summer: 32, monsoon: 90, "post-monsoon": 70 } },
  { name: "KRS (Krishna Raja Sagara)", state: "Karnataka", x: 40, y: 68, capacity: 1400, levels: { winter: 55, summer: 28, monsoon: 85, "post-monsoon": 65 } },
  // Tamil Nadu — far south
  { name: "Mettur", state: "Tamil Nadu", x: 46, y: 72, capacity: 2648, levels: { winter: 48, summer: 20, monsoon: 75, "post-monsoon": 58 } },
  { name: "Vaigai", state: "Tamil Nadu", x: 48, y: 78, capacity: 194, levels: { winter: 42, summer: 15, monsoon: 70, "post-monsoon": 50 } },
  // Gujarat — west
  { name: "Sardar Sarovar", state: "Gujarat", x: 27, y: 44, capacity: 9460, levels: { winter: 65, summer: 38, monsoon: 92, "post-monsoon": 75 } },
  { name: "Ukai", state: "Gujarat", x: 30, y: 47, capacity: 7092, levels: { winter: 60, summer: 33, monsoon: 88, "post-monsoon": 70 } },
  // Madhya Pradesh — central
  { name: "Tawa", state: "Madhya Pradesh", x: 44, y: 41, capacity: 1995, levels: { winter: 58, summer: 30, monsoon: 85, "post-monsoon": 68 } },
  { name: "Bargi", state: "Madhya Pradesh", x: 48, y: 39, capacity: 3921, levels: { winter: 55, summer: 28, monsoon: 82, "post-monsoon": 64 } },
  // Kerala — SW tip
  { name: "Idukki", state: "Kerala", x: 39, y: 78, capacity: 1996, levels: { winter: 72, summer: 45, monsoon: 92, "post-monsoon": 80 } },
  { name: "Banasura Sagar", state: "Kerala", x: 37, y: 75, capacity: 207, levels: { winter: 68, summer: 42, monsoon: 90, "post-monsoon": 76 } },
];

export const getHeatColor = (level: number): string => {
  if (level >= 75) return "hsl(var(--chart-2))";     // blue-teal — healthy
  if (level >= 50) return "hsl(var(--chart-4))";      // green-ish — moderate
  if (level >= 30) return "hsl(var(--warning))";      // amber — stress
  return "hsl(var(--destructive))";                    // red — critical
};

export const getStatusLabel = (level: number): string => {
  if (level >= 75) return "Healthy";
  if (level >= 50) return "Moderate";
  if (level >= 30) return "Stress";
  return "Critical";
};
