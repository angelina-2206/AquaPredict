import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Download, Loader2, AlertTriangle } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAppState } from "@/lib/StateContext";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalysis } from "@/lib/api";

const Reports = () => {
  const { selectedState } = useAppState();

  const { data: analysis, isLoading, isError } = useQuery({
    queryKey: ['analysis', selectedState],
    queryFn: () => fetchAnalysis(selectedState, 12, 0.0),
  });

  const handleExportPDF = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Generating report data...</p>
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

  // Calculate some strings for the report
  const currentRisk = analysis.kpis.risk_indicator;
  const currentLevelPct = analysis.kpis.current_reservoir_level_pct;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Reports ({selectedState})</h1>
          <p className="text-sm text-muted-foreground">Generate and export policy-ready reports.</p>
        </div>
        <Button size="sm" onClick={handleExportPDF} className="print:hidden">
          <Download className="mr-1.5 h-3.5 w-3.5" />
          Export PDF
        </Button>
      </div>

      {/* Executive Summary */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-secondary" />
            <CardTitle className="text-base">Executive Summary</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-relaxed text-muted-foreground">
          <p>
            This report presents the findings of the AquaPredict water demand forecasting and reservoir storage analysis 
            for <strong className="text-foreground">{selectedState}</strong> during the upcoming 12-month period.
          </p>
          <p>
            <span className="font-semibold text-foreground">Key Finding 1:</span> The projected initial storage sits at roughly {currentLevelPct.toFixed(1)}%. 
            Water constraints and capacity gaps have produced an overall risk indication of: <strong className="text-foreground">{currentRisk}</strong>.
          </p>
          <p>
            <span className="font-semibold text-foreground">Key Finding 2:</span> Depending on the forecasted demand against the local supply limits, 
            storage may enter stress zones. Time-series ARIMA evaluation was executed to provide localized predictions.
          </p>
          <p>
            <span className="font-semibold text-foreground">Recommendation:</span> Implement seasonal demand management strategies where supply-demand 
            gaps manifest and consider infrastructure investment for long-term drought resilience.
          </p>
        </CardContent>
      </Card>

      {/* Forecast Summary Table */}
      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-base">Demand Forecast Summary</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Month</TableHead>
                <TableHead className="text-right">Demand (ML)</TableHead>
                <TableHead className="text-right">Storage (%)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {analysis.charts.supplyDemand.map((row, i) => {
                const storageData = analysis.charts.reservoirStorage[i];
                const storagePct = storageData ? Math.round((storageData.storage / storageData.capacity) * 100) : 0;
                return (
                  <TableRow key={row.month}>
                    <TableCell className="font-medium">{row.month}</TableCell>
                    <TableCell className="text-right">{Math.round(row.demand)}</TableCell>
                    <TableCell className="text-right">{storagePct}%</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2"><CardTitle className="text-base">Methodology</CardTitle></CardHeader>
        <CardContent className="text-sm leading-relaxed text-muted-foreground">
          <p>
            Water demand forecasting utilized ARIMA time-series decomposition. Reservoir simulation employed a 
            mass-balance approach integrating projected inflow from rainfall correlation models with forecasted demand. 
            Live Python endpoints compute models at `<code className="text-xs">/api/analysis/{selectedState}</code>`.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
