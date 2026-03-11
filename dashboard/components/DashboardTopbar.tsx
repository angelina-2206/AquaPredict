import { SidebarTrigger } from "@/components/ui/sidebar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Download, Droplets, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchStates } from "@/lib/api";
import { useAppState } from "@/lib/StateContext";

export function DashboardTopbar() {
  const { selectedState, setSelectedState, selectedYear, setSelectedYear } = useAppState();

  const { data: states, isLoading } = useQuery({
    queryKey: ['states'],
    queryFn: fetchStates,
  });

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-4">
      <div className="flex items-center gap-3">
        <SidebarTrigger />
        <div className="hidden items-center gap-2 sm:flex">
          <Droplets className="h-4 w-4 text-secondary" />
          <span className="text-sm font-semibold text-foreground">AquaPredict</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {isLoading ? (
          <div className="flex items-center space-x-2 text-xs text-muted-foreground mr-4">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Loading Regions...</span>
          </div>
        ) : (
          <Select value={selectedState} onValueChange={setSelectedState}>
            <SelectTrigger className="h-8 w-[180px] text-xs">
              <SelectValue placeholder="State" />
            </SelectTrigger>
            <SelectContent>
              {(states as string[] | undefined)?.map((stateName: string) => (
                 <SelectItem key={stateName} value={stateName}>{stateName}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        <Select value={selectedYear} onValueChange={setSelectedYear}>
          <SelectTrigger className="h-8 w-[90px] text-xs">
            <SelectValue placeholder="Year" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="2024">2024</SelectItem>
            <SelectItem value="2025">2025</SelectItem>
            <SelectItem value="2026">2026</SelectItem>
          </SelectContent>
        </Select>

        <Button variant="outline" size="sm" className="h-8 text-xs">
          <Download className="mr-1.5 h-3.5 w-3.5" />
          Export
        </Button>
      </div>
    </header>
  );
}
