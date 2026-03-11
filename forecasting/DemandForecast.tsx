import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart,
} from "recharts";
import { Upload, Loader2, AlertTriangle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalysis } from "@/lib/api";
import { useAppState } from "@/lib/StateContext";

const DemandForecast = () => {
  const { selectedState } = useAppState();

  const { data: analysis, isLoading, isError } = useQuery({
    queryKey: ['analysis', selectedState],
    queryFn: () => fetchAnalysis(selectedState, 12, 0.0),
  });

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Running ARIMA models...</p>
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
      <h1 className="text-2xl font-bold text-foreground">Demand Forecast ({selectedState})</h1>
      <p className="text-sm text-muted-foreground">Predict future water demand using time-series models.</p>
    </div>

    {/* Controls */}
    <Card>
      <CardContent className="flex flex-wrap items-end gap-4 p-5">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Upload Historical Data</label>
          <Button variant="outline" size="sm"><Upload className="mr-1.5 h-3.5 w-3.5" />Upload CSV</Button>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Model</label>
          <Select defaultValue="arima">
            <SelectTrigger className="h-8 w-[160px] text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="linear">Linear Regression</SelectItem>
              <SelectItem value="arima">ARIMA</SelectItem>
              <SelectItem value="lstm">LSTM (Placeholder)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Forecast Horizon</label>
          <Select defaultValue="12">
            <SelectTrigger className="h-8 w-[130px] text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="6">6 Months</SelectItem>
              <SelectItem value="12">1 Year</SelectItem>
              <SelectItem value="60">5 Years</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button size="sm" className="h-8">Run Forecast</Button>
      </CardContent>
    </Card>

    {/* Chart with confidence interval */}
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-base">Forecast with Confidence Interval</CardTitle></CardHeader>
      <CardContent>
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={analysis.charts.demandForecast}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Area type="monotone" dataKey="upper" fill="hsl(var(--chart-2))" fillOpacity={0.08} stroke="none" name="Upper CI" />
              <Area type="monotone" dataKey="lower" fill="hsl(var(--background))" fillOpacity={1} stroke="none" name="Lower CI" />
              <Line type="monotone" dataKey="actual" stroke="hsl(var(--chart-1))" strokeWidth={2} name="Actual" dot={{ r: 3 }} />
              <Line type="monotone" dataKey="forecast" stroke="hsl(var(--chart-2))" strokeWidth={2} strokeDasharray="5 5" name="Forecast" dot={{ r: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>

    <div className="grid gap-6 lg:grid-cols-3">
      {/* Accuracy */}
      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-base">Model Performance</CardTitle></CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground">Model</span><span className="font-medium">ARIMA(1,1,1)</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">RMSE</span><span className="font-medium">{analysis.kpis.metrics.RMSE.toFixed(2)} ML</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">MAE</span><span className="font-medium">{analysis.kpis.metrics.MAE.toFixed(2)} ML</span></div>
        </CardContent>
      </Card>

      {/* Interpretation */}
      <Card className="lg:col-span-2">
        <CardHeader className="pb-2"><CardTitle className="text-base">Model Interpretation</CardTitle></CardHeader>
        <CardContent className="text-sm leading-relaxed text-muted-foreground">
          The ARIMA(1,1,1) Python backend model captures seasonal water demand patterns. 
          The confidence intervals illustrate the bounds of uncertainty over the forecast horizon.
        </CardContent>
      </Card>
    </div>

    {/* Data Table */}
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-base">Forecast Data</CardTitle></CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Month</TableHead>
              <TableHead className="text-right">Actual (ML)</TableHead>
              <TableHead className="text-right">Forecast (ML)</TableHead>
              <TableHead className="text-right">Lower CI</TableHead>
              <TableHead className="text-right">Upper CI</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {analysis.charts.demandForecast.map((row) => (
              <TableRow key={row.month}>
                <TableCell className="font-medium">{row.month}</TableCell>
                <TableCell className="text-right">{row.actual}</TableCell>
                <TableCell className="text-right">{row.forecast}</TableCell>
                <TableCell className="text-right">{row.lower}</TableCell>
                <TableCell className="text-right">{row.upper}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
  );
};

export default DemandForecast;
