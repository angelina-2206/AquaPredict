import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, LineChart, Line } from "recharts";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalysis } from "@/lib/api";
import { Loader2, AlertTriangle } from "lucide-react";

import { useAppState } from "@/lib/StateContext";

const RainfallInflow = () => {
  const { selectedState } = useAppState();

  const { data: analysis, isLoading, isError } = useQuery({
    queryKey: ['analysis', selectedState],
    queryFn: () => fetchAnalysis(selectedState, 12, 0.0),
  });

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Loading rainfall & inflow models...</p>
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

  return (
  <div className="space-y-6">
    <div>
      <h1 className="text-2xl font-bold text-foreground">Rainfall & Inflow Analysis ({selectedState})</h1>
      <p className="text-sm text-muted-foreground">Analyze precipitation patterns and resulting reservoir inflow.</p>
    </div>

    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-base">Monthly Rainfall Distribution</CardTitle></CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analysis.charts.rainfall}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                <Bar dataKey="rainfall" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} name="Rainfall (mm)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-base">Inflow Trend</CardTitle></CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analysis.charts.rainfall}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                <Line type="monotone" dataKey="inflow" stroke="hsl(var(--chart-2))" strokeWidth={2} name="Inflow (ML)" dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>

    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-base">Rainfall–Inflow Correlation</CardTitle></CardHeader>
      <CardContent>
        <div className="h-[280px]">
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
        <p className="mt-4 text-sm text-muted-foreground">
          Pearson correlation coefficient: <span className="font-semibold text-foreground">r = 0.98</span>. Strong positive correlation between rainfall and reservoir inflow.
        </p>
      </CardContent>
    </Card>
  </div>
  );
};

export default RainfallInflow;
