import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine,
} from "recharts";
import { riskLevel } from "@/data/sampleData";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalysis } from "@/lib/api";
import { Loader2, AlertTriangle } from "lucide-react";

import { useAppState } from "@/lib/StateContext";

const SupplyDemandAnalysis = () => {
  const { selectedState } = useAppState();

  const { data: analysis, isLoading, isError } = useQuery({
    queryKey: ['analysis', selectedState],
    queryFn: () => fetchAnalysis(selectedState, 12, 0.0),
  });

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Analyzing supply and demand gaps...</p>
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

  const supplyDemandData = analysis.charts.supplyDemand;
  const shortageMonths = supplyDemandData.filter(d => d.gap < 0);
  const firstShortage = shortageMonths.length > 0 ? shortageMonths[0].month : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Supply–Demand Analysis ({selectedState})</h1>
        <p className="text-sm text-muted-foreground">Identify gaps between water supply capacity and projected demand.</p>
      </div>

      {/* Overlay Chart */}
      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-base">Supply vs Demand</CardTitle></CardHeader>
        <CardContent>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={supplyDemandData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="supply" stroke="hsl(var(--chart-2))" strokeWidth={2} name="Supply (ML)" dot={{ r: 3 }} />
                <Line type="monotone" dataKey="demand" stroke="hsl(var(--chart-5))" strokeWidth={2} name="Demand (ML)" dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Gap Visualization */}
      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-base">Supply–Demand Gap</CardTitle></CardHeader>
        <CardContent>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={supplyDemandData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
                <ReferenceLine y={0} stroke="hsl(var(--foreground))" strokeWidth={1} />
                <Area
                  type="monotone"
                  dataKey="gap"
                  stroke="hsl(var(--chart-2))"
                  fill="hsl(var(--chart-2))"
                  fillOpacity={0.15}
                  name="Gap (ML)"
                  dot={(props: any) => {
                    const { cx, cy, payload } = props;
                    const color = payload.gap < 0 ? "hsl(var(--destructive))" : payload.gap < 10 ? "hsl(var(--warning))" : "hsl(var(--chart-2))";
                    return <circle cx={cx} cy={cy} r={4} fill={color} stroke={color} />;
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Risk Timeline */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Risk Prediction Timeline</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {supplyDemandData.map(d => {
                const r = riskLevel(d.gap);
                return (
                  <div key={d.month} className="flex items-center justify-between text-sm">
                    <span className="font-medium">{d.month}</span>
                    <Badge variant={r === "High" ? "destructive" : r === "Moderate" ? "outline" : "secondary"} className="text-xs">
                      {r}
                    </Badge>
                  </div>
                );
              })}
            </div>
            {firstShortage && (
              <div className="mt-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                ⚠ Projected first shortage month: <span className="font-bold">{firstShortage}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Policy Insights */}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Suggested Policy Insights</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <div className="rounded-md border-l-2 border-secondary p-3">
              <p className="font-semibold text-foreground">Demand Management</p>
              <p>Implement water-use restrictions during May–September when demand exceeds supply capacity.</p>
            </div>
            <div className="rounded-md border-l-2 border-secondary p-3">
              <p className="font-semibold text-foreground">Infrastructure Investment</p>
              <p>Consider augmenting reservoir capacity or establishing inter-basin transfer agreements for drought resilience.</p>
            </div>
            <div className="rounded-md border-l-2 border-warning p-3">
              <p className="font-semibold text-foreground">Early Warning</p>
              <p>Deploy real-time monitoring at reservoir sites with automated alerts at 45% and 30% capacity thresholds.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SupplyDemandAnalysis;
