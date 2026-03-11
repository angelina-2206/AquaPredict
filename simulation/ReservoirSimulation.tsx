import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { Badge } from "@/components/ui/badge";
import WaterTank from "@/components/WaterTank";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalysis } from "@/lib/api";
import { Loader2, AlertTriangle } from "lucide-react";

import { useAppState } from "@/lib/StateContext";

const ReservoirSimulation = () => {
  const { selectedState } = useAppState();

  const { data: analysis, isLoading, isError } = useQuery({
    queryKey: ['analysis', selectedState],
    queryFn: () => fetchAnalysis(selectedState, 12, 0.0),
  });

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Running physical reservoir simulations...</p>
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

  // Map volume to percentage for the charts and tanks
  const mappedStorageData = analysis.charts.reservoirStorage.map(d => ({
    ...d,
    storagePct: (d.storage / d.capacity) * 100
  }));

  const getTankData = (idx: number) => {
    const dataNum = Math.min(idx, mappedStorageData.length - 1);
    return mappedStorageData[dataNum] || { storagePct: 0, month: "N/A" };
  };

  return (
  <div className="space-y-6">
    <div>
      <h1 className="text-2xl font-bold text-foreground">Reservoir Simulation ({selectedState})</h1>
      <p className="text-sm text-muted-foreground">Simulate reservoir storage under projected inflow and demand scenarios.</p>
    </div>

    {/* Inputs */}
    <Card>
      <CardContent className="flex flex-wrap items-end gap-4 p-5">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Initial Storage (%)</label>
          <Input type="number" defaultValue={78} className="h-8 w-[100px] text-xs" />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Monthly Inflow (ML)</label>
          <Input type="number" defaultValue={36} className="h-8 w-[100px] text-xs" />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Monthly Demand (ML)</label>
          <Input type="number" defaultValue={57} className="h-8 w-[100px] text-xs" />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Capacity (ML)</label>
          <Input type="number" defaultValue={1200} className="h-8 w-[100px] text-xs" />
        </div>
        <Button size="sm" className="h-8">Run Simulation</Button>
      </CardContent>
    </Card>

    {/* Animated Water Level Tanks */}
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Live Storage Levels</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap justify-center gap-8">
          <WaterTank level={getTankData(0).storagePct || 0} label={getTankData(0).month} />
          <WaterTank level={getTankData(3).storagePct || 0} label={getTankData(3).month} />
          <WaterTank level={getTankData(6).storagePct || 0} label={getTankData(6).month} />
          <WaterTank level={getTankData(9).storagePct || 0} label={getTankData(9).month} />
          <WaterTank level={getTankData(11).storagePct || 0} label={getTankData(11).month} />
        </div>
      </CardContent>
    </Card>

    {/* Simulation Chart */}
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Storage Simulation</CardTitle>
          <div className="flex gap-2">
            <Badge variant="outline" className="border-warning text-warning text-xs">Stress Zone: 30–45%</Badge>
            <Badge variant="outline" className="border-destructive text-destructive text-xs">Critical: &lt;30%</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[340px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={mappedStorageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" domain={[0, 100]} />
              <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
              <ReferenceLine y={30} stroke="hsl(var(--destructive))" strokeDasharray="4 4" label={{ value: "Critical", position: "right", fontSize: 11, fill: "hsl(var(--destructive))" }} />
              <ReferenceLine y={45} stroke="hsl(var(--warning))" strokeDasharray="4 4" label={{ value: "Stress", position: "right", fontSize: 11, fill: "hsl(var(--warning))" }} />
              <Area
                type="monotone"
                dataKey="storagePct"
                stroke="hsl(var(--chart-2))"
                strokeWidth={2}
                fill="hsl(var(--chart-2))"
                fillOpacity={0.15}
                name="Storage (%)"
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  const color = payload.storagePct < 30 ? "hsl(var(--destructive))" : payload.storagePct < 45 ? "hsl(var(--warning))" : "hsl(var(--chart-2))";
                  return <circle cx={cx} cy={cy} r={4} fill={color} stroke={color} />;
                }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-base">Simulation Summary</CardTitle></CardHeader>
      <CardContent className="space-y-2 text-sm text-muted-foreground">
        <p>Reservoir storage is initially <span className="font-semibold text-foreground">{analysis.kpis.current_reservoir_level_pct.toFixed(1)}%</span>.</p>
        <p>This dynamic simulation is computed by our advanced Python hydrological model balancing forecasted demand and historical inflow variations.</p>
        <p>Risk Indicator sets the priority of management: <span className="font-semibold text-warning">{analysis.kpis.risk_indicator}</span>.</p>
      </CardContent>
    </Card>
  </div>
  );
};

export default ReservoirSimulation;
