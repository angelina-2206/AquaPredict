import { motion } from "framer-motion";

interface WaterTankProps {
  level: number; // 0-100
  label?: string;
}

const WaterTank = ({ level, label }: WaterTankProps) => {
  const clampedLevel = Math.max(0, Math.min(100, level));
  const color =
    clampedLevel < 30
      ? "hsl(var(--destructive))"
      : clampedLevel < 45
      ? "hsl(var(--warning))"
      : "hsl(var(--chart-2))";

  return (
    <div className="flex flex-col items-center gap-2">
      {label && (
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
      )}
      <div className="relative h-[200px] w-[90px] rounded-b-2xl rounded-t-md border-2 border-border bg-muted/30 overflow-hidden">
        {/* Water fill */}
        <motion.div
          className="absolute bottom-0 left-0 right-0 rounded-b-xl"
          initial={{ height: 0 }}
          animate={{ height: `${clampedLevel}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          style={{ background: color, opacity: 0.7 }}
        />
        {/* Wave SVG overlay */}
        <motion.div
          className="absolute left-0 right-0"
          initial={{ bottom: 0 }}
          animate={{ bottom: `${clampedLevel}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          style={{ transform: "translateY(50%)" }}
        >
          <svg viewBox="0 0 90 12" className="w-full" preserveAspectRatio="none">
            <motion.path
              d="M0 6 Q 15 0, 30 6 T 60 6 T 90 6 V 12 H 0 Z"
              fill={color}
              fillOpacity={0.7}
              animate={{ d: [
                "M0 6 Q 15 0, 30 6 T 60 6 T 90 6 V 12 H 0 Z",
                "M0 6 Q 15 12, 30 6 T 60 6 T 90 6 V 12 H 0 Z",
                "M0 6 Q 15 0, 30 6 T 60 6 T 90 6 V 12 H 0 Z",
              ] }}
              transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            />
          </svg>
        </motion.div>
        {/* Level text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold text-foreground drop-shadow-sm">
            {Math.round(clampedLevel)}%
          </span>
        </div>
        {/* Threshold markers */}
        <div className="absolute left-0 right-0 border-t border-dashed border-destructive/60" style={{ bottom: "30%" }} />
        <div className="absolute left-0 right-0 border-t border-dashed border-warning/60" style={{ bottom: "45%" }} />
      </div>
      <div className="flex gap-3 text-[10px] text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-destructive" /> 30%
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-warning" /> 45%
        </span>
      </div>
    </div>
  );
};

export default WaterTank;
