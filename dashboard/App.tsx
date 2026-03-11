import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppStateProvider } from "./lib/StateContext";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import DashboardLayout from "./pages/DashboardLayout";
import Overview from "./Overview";
import DemandForecast from "../forecasting/DemandForecast";
import RainfallInflow from "../analysis/RainfallInflow";
import ReservoirSimulation from "../simulation/ReservoirSimulation";
import SupplyDemandAnalysis from "../analysis/SupplyDemandAnalysis";
import Reports from "./Reports";
import SettingsPage from "./Settings";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AppStateProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<Overview />} />
              <Route path="demand" element={<DemandForecast />} />
              <Route path="rainfall" element={<RainfallInflow />} />
              <Route path="reservoir" element={<ReservoirSimulation />} />
              <Route path="supply-demand" element={<SupplyDemandAnalysis />} />
              <Route path="reports" element={<Reports />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AppStateProvider>
  </QueryClientProvider>
);

export default App;
