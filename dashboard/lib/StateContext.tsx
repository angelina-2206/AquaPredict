import React, { createContext, useContext, useState } from "react";

interface AppState {
  selectedState: string;
  selectedYear: string;
  setSelectedState: (state: string) => void;
  setSelectedYear: (year: string) => void;
}

const AppStateContext = createContext<AppState | undefined>(undefined);

export const AppStateProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedState, setSelectedState] = useState<string>("Andhra Pradesh");
  const [selectedYear, setSelectedYear] = useState<string>("2024");

  return (
    <AppStateContext.Provider value={{ selectedState, selectedYear, setSelectedState, setSelectedYear }}>
      {children}
    </AppStateContext.Provider>
  );
};

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used within an AppStateProvider");
  }
  return context;
};
