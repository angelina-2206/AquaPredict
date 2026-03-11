import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { BarChart3, CloudRain, Waves, AlertTriangle, LineChart } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  { icon: LineChart, title: "Demand Forecasting Module", desc: "Time-series models predict future water demand with confidence intervals." },
  { icon: CloudRain, title: "Rainfall & Inflow Analysis", desc: "Analyze precipitation patterns and reservoir inflow projections." },
  { icon: Waves, title: "Reservoir Storage Simulation", desc: "Simulate storage behavior under varying inflow and demand scenarios." },
  { icon: AlertTriangle, title: "Supply–Demand Gap Detection", desc: "Identify critical shortage periods and policy intervention windows." },
  { icon: BarChart3, title: "Interactive Visual Analytics", desc: "Rich, accessible charts for transparent decision-making." },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.5 } }),
};

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="relative overflow-hidden bg-primary text-primary-foreground">
        {/* Water wave SVG background */}
        <div className="absolute inset-0 opacity-10">
          <svg className="absolute bottom-0 w-full" viewBox="0 0 1440 320" preserveAspectRatio="none">
            <path fill="currentColor" d="M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,138.7C672,128,768,160,864,181.3C960,203,1056,213,1152,197.3C1248,181,1344,139,1392,117.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" />
          </svg>
        </div>

        <div className="container relative z-10 mx-auto px-6 py-24 md:py-32 lg:py-40">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="max-w-3xl"
          >
            <p className="mb-3 text-sm font-medium uppercase tracking-widest opacity-70">
              Sustainable Water Intelligence
            </p>
            <h1 className="mb-4 text-4xl font-bold leading-tight md:text-5xl lg:text-6xl">
              AquaPredict
            </h1>
            <p className="mb-2 text-lg font-medium opacity-90 md:text-xl">
              A Predictive Software System for Water Demand Forecasting and Reservoir Storage Analysis
            </p>
            <p className="mb-8 max-w-2xl text-base leading-relaxed opacity-75">
              Combining time-series forecasting with reservoir simulation to support evidence-based water resource management and policy planning.
            </p>
            <Button
              size="lg"
              variant="secondary"
              className="text-base font-semibold"
              onClick={() => navigate("/dashboard")}
            >
              Launch Dashboard
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="mb-12 text-center"
        >
          <motion.h2 variants={fadeUp} custom={0} className="mb-3 text-3xl font-bold text-foreground">
            Core Capabilities
          </motion.h2>
          <motion.p variants={fadeUp} custom={1} className="mx-auto max-w-xl text-muted-foreground">
            Integrated modules for comprehensive water resource analysis and forecasting.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              variants={fadeUp}
              custom={i + 2}
              className="group rounded-lg border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-md bg-secondary/10">
                <f.icon className="h-5 w-5 text-secondary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-card-foreground">{f.title}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Research Foundation */}
      <section className="border-t bg-muted/50">
        <div className="container mx-auto px-6 py-16">
          <h2 className="mb-8 text-2xl font-bold text-foreground">Research Foundation</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { title: "Time-Series Forecasting", desc: "ARIMA and LSTM-based models for seasonal and long-term water demand prediction." },
              { title: "Reservoir Simulation", desc: "Mass-balance reservoir models incorporating variable inflow, demand, and capacity constraints." },
              { title: "Climate Variability", desc: "Integration of rainfall variability and climate projections into forecasting frameworks." },
            ].map((item) => (
              <div key={item.title} className="rounded-md border-l-2 border-secondary bg-card p-5">
                <h3 className="mb-2 font-semibold text-card-foreground">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-card py-8">
        <div className="container mx-auto px-6 text-center text-sm text-muted-foreground">
          AquaPredict © 2026 | Sustainable Water Intelligence Platform &middot; v1.0.0
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
