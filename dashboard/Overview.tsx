import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalysis } from "@/lib/api";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { Droplets, TrendingUp, CloudRain, AlertTriangle, Loader2 } from "lucide-react";
import IndiaReservoirMap from "@/components/IndiaReservoirMap";

const StatCard = ({ title, value, subtitle, icon: Icon, variant = "default" }: {
  title: string; value: string; subtitle: string; icon: React.ElementType;
  variant?: "default" | "warning" | "destructive";
}) => (
  <Card>
    <CardContent className="flex items-start gap-4 p-5">
      <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
        variant === "destructive" ? "bg-destructive/10 text-destructive" :
        variant === "warning" ? "bg-warning/10 text-warning" :
        "bg-secondary/10 text-secondary"
      }`}>
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <p className="text-xs font-medium text-muted-foreground">{title}</p>
        <p className="text-2xl font-bold text-foreground">{value}</p>
        <p className="text-xs text-muted-foreground">{subtitle}</p>
      </div>
    </CardContent>
  </Card>
);

import { useAppState } from "@/lib/StateContext";

const Overview = () => {
  const { selectedState } = useAppState();

  const { data: analysis, isLoading, isError } = useQuery({
    queryKey: ['analysis', selectedState],
    queryFn: () => fetchAnalysis(selectedState, 12, 0.0),
  });

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Running AI forecasting models on AquaPredict pipeline...</p>
      </div>
    );
  }

  if (isError || !analysis) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4 text-destructive">
        <AlertTriangle className="h-10 w-10" />
        <p>Error loading analytical data from Python backend.</p>
      </div>
    );
  }

  const risk = analysis.kpis.risk_indicator;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Overview ({selectedState})</h1>
        <p className="text-sm text-muted-foreground">Water resource analytics summary for the current period.</p>
      </div>

      {/* Stat Widgets */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard icon={Droplets} title="Current Reservoir Level" value={`${analysis.kpis.current_reservoir_level_pct.toFixed(0)}%`} subtitle={`${analysis.kpis.current_reservoir_level} / ${analysis.kpis.capacity} ML`} variant={analysis.kpis.current_reservoir_level_pct < 30 ? "destructive" : "default"} />
      <StatCard icon={TrendingUp} title="Forecasted Demand (12mo)" value={`${analysis.kpis.forecasted_demand} ML`} subtitle={`Avg ${analysis.kpis.avg_monthly_demand} ML/month`} />
      <StatCard icon={CloudRain} title="Avg Monthly Inflow" value={`${analysis.kpis.avg_monthly_inflow} ML`} subtitle="Trailing 12 months average" />
      <StatCard
        icon={AlertTriangle}
        title="Risk Indicator"
        value={risk}
        subtitle={risk === "Critical" ? "Immediate action needed" : risk === "Moderate" ? "Monitor closely" : "Within safe range"}
        variant={risk === "Critical" ? "destructive" : risk === "Moderate" ? "warning" : "default"}
      />
    </div>

    {/* Charts */}
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Demand Forecast */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Water Demand Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analysis.charts.demandForecast}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="actual" stroke="hsl(var(--chart-1))" strokeWidth={2} name="Actual" dot={false} />
                <Line type="monotone" dataKey="forecast" stroke="hsl(var(--chart-2))" strokeWidth={2} strokeDasharray="5 5" name="Forecast" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Reservoir Storage */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Reservoir Storage Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analysis.charts.reservoirStorage}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                <Area type="monotone" dataKey="storage" fill="hsl(var(--chart-2))" fillOpacity={0.2} stroke="hsl(var(--chart-2))" strokeWidth={2} name="Storage (%)" />
                <Line type="monotone" dataKey="threshold" stroke="hsl(var(--chart-5))" strokeWidth={1.5} strokeDasharray="4 4" name="Critical Threshold" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Rainfall */}
      <Card className="lg:col-span-2">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Rainfall Distribution & Inflow</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analysis.charts.rainfall}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="rainfall" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} name="Rainfall (mm)" />
                <Bar dataKey="inflow" fill="hsl(var(--chart-2))" radius={[4, 4, 0, 0]} name="Inflow (ML)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>

    {/* India Reservoir Heatmap */}
    <IndiaReservoirMap />
  </div>
  );
};

export default Overview;
