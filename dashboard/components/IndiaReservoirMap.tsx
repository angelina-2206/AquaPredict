import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import IndiaMapSVG from "react-svgmap-india";
import { reservoirs, seasons, getHeatColor, getStatusLabel, type Season } from "@/data/indianStates";

const IndiaReservoirMap = () => {
  const [season, setSeason] = useState<Season>("monsoon");
  const [hoveredReservoir, setHoveredReservoir] = useState<string | null>(null);
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);

  const handleStateClick = (stateName: string) => {
    setSelectedState(prev => prev === stateName ? null : stateName);
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="text-base">India Reservoir Heatmap</CardTitle>
          <Select value={season} onValueChange={(v) => setSeason(v as Season)}>
            <SelectTrigger className="h-8 w-[180px] text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {seasons.map((s) => (
                <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {/* Legend */}
        <div className="mb-4 flex flex-wrap gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: "hsl(var(--chart-2))" }} /> ≥75% Healthy
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: "hsl(var(--chart-4))" }} /> 50–74% Moderate
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: "hsl(var(--warning))" }} /> 30–49% Stress
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: "hsl(var(--destructive))" }} /> &lt;30% Critical
          </span>
        </div>

        {/* Map container */}
        <div
          ref={mapContainerRef}
          className="relative mx-auto max-w-[500px] rounded-xl border border-border bg-muted/20 overflow-hidden"
        >
          {/* India SVG Map with state boundaries */}
          <div className="india-map-wrapper">
            <IndiaMapSVG
              size="100%"
              mapColor="hsl(var(--muted))"
              strokeColor="hsl(var(--border))"
              strokeWidth="0.5"
              hoverColor="hsl(var(--accent))"
              onClick={handleStateClick}
            />
          </div>

          {/* Reservoir dots overlay */}
          <div className="absolute inset-0 pointer-events-none">
          <AnimatePresence>
            {reservoirs.map((r) => {
              const level = r.levels[season];
              const color = getHeatColor(level);
                const isHovered = hoveredReservoir === r.name;

                return (
                  <motion.div
                    key={`${r.name}-${season}`}
                    className="absolute cursor-pointer pointer-events-auto"
                    style={{ left: `${r.x}%`, top: `${r.y}%`, transform: "translate(-50%, -50%)" }}
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0, opacity: 0 }}
                    transition={{ duration: 0.4, delay: Math.random() * 0.3 }}
                    onMouseEnter={() => setHoveredReservoir(r.name)}
                    onMouseLeave={() => setHoveredReservoir(null)}
                  >
                    {/* Pulse ring */}
                    <motion.div
                      className="absolute rounded-full"
                      style={{
                        width: isHovered ? 28 : 20,
                        height: isHovered ? 28 : 20,
                        background: color,
                        opacity: 0.2,
                        left: "50%",
                        top: "50%",
                        transform: "translate(-50%, -50%)",
                      }}
                      animate={{ scale: [1, 1.5, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                    {/* Dot */}
                    <motion.div
                      className="relative rounded-full border border-background/50"
                      style={{
                        width: isHovered ? 14 : 10,
                        height: isHovered ? 14 : 10,
                        background: color,
                      }}
                      animate={{ scale: isHovered ? 1.3 : 1 }}
                    />

                    {/* Tooltip */}
                    <AnimatePresence>
                      {isHovered && (
                        <motion.div
                          className="absolute bottom-full left-1/2 z-10 mb-2 w-48 -translate-x-1/2 rounded-lg border border-border bg-card p-2.5 shadow-lg"
                          initial={{ opacity: 0, y: 4 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 4 }}
                        >
                          <p className="text-xs font-semibold text-foreground">{r.name}</p>
                          <p className="text-[10px] text-muted-foreground">{r.state}</p>
                          <div className="mt-1.5 flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">Level: <span className="font-semibold text-foreground">{level}%</span></span>
                            <Badge variant={level >= 50 ? "secondary" : level >= 30 ? "outline" : "destructive"} className="text-[10px] px-1.5 py-0">
                              {getStatusLabel(level)}
                            </Badge>
                          </div>
                          <div className="mt-1 h-1.5 w-full rounded-full bg-muted">
                            <div className="h-full rounded-full" style={{ width: `${level}%`, background: color }} />
                          </div>
                          <p className="mt-1 text-[10px] text-muted-foreground">Capacity: {r.capacity.toLocaleString()} MCM</p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </div>

        {/* Season summary stats */}
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {["Healthy", "Moderate", "Stress", "Critical"].map((status) => {
            const count = reservoirs.filter((r) => getStatusLabel(r.levels[season]) === status).length;
            return (
              <div key={status} className="rounded-lg border border-border bg-muted/20 p-2.5 text-center">
                <p className="text-lg font-bold text-foreground">{count}</p>
                <p className="text-[10px] text-muted-foreground">{status}</p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default IndiaReservoirMap;
