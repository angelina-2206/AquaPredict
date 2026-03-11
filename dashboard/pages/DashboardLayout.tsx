import { Outlet } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { DashboardSidebar } from "@/components/DashboardSidebar";
import { DashboardTopbar } from "@/components/DashboardTopbar";

const DashboardLayout = () => {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <DashboardSidebar />
        <div className="flex flex-1 flex-col">
          <DashboardTopbar />
          <main className="flex-1 overflow-auto bg-background p-6">
            <Outlet />
          </main>
          <footer className="border-t bg-card px-6 py-3 text-center text-xs text-muted-foreground">
            AquaPredict © 2026 | Sustainable Water Intelligence Platform &middot; v1.0.0
          </footer>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default DashboardLayout;
