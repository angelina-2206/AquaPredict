"""
Reservoir storage simulation module for AquaPredict system.
Implements water balance model for reservoir storage forecasting.
"""

import pandas as pd
import numpy as np

class ReservoirSimulator:
    """
    A class to simulate reservoir storage dynamics using water balance modeling.
    """
    
    def __init__(self, initial_storage=None, storage_capacity=None):
        """
        Initialize the reservoir simulator.
        
        Args:
            initial_storage (float): Initial storage level
            storage_capacity (float): Maximum storage capacity
        """
        self.initial_storage = initial_storage
        self.storage_capacity = storage_capacity
        self.simulation_results = None
    
    def water_balance_model(self, storage_t, inflow, demand, losses=0.1):
        """
        Calculate storage for next time period using water balance equation.
        
        Storage(t+1) = Storage(t) + Inflow - Demand - Losses
        
        Args:
            storage_t (float): Current storage level
            inflow (float): Inflow volume (rainfall/runoff)
            demand (float): Water demand
            losses (float): Loss percentage (evaporation, seepage, etc.)
            
        Returns:
            float: Storage level for next period
        """
        # Calculate losses as percentage of current storage
        loss_volume = storage_t * losses
        
        # Water balance equation
        storage_t1 = storage_t + inflow - demand - loss_volume
        
        # Ensure storage doesn't go negative or exceed capacity
        storage_t1 = max(0, storage_t1)
        if self.storage_capacity:
            storage_t1 = min(storage_t1, self.storage_capacity)
            
        return storage_t1
    
    def simulate_storage(self, forecast_periods, inflow_data, demand_data, 
                        initial_storage=None, losses=0.1):
        """
        Simulate reservoir storage over forecast horizon.
        
        Args:
            forecast_periods (int): Number of periods to simulate
            inflow_data (list or array): Inflow values for each period
            demand_data (list or array): Demand values for each period
            initial_storage (float): Initial storage level
            losses (float): Loss percentage
            
        Returns:
            pd.DataFrame: Simulation results
        """
        if initial_storage is None:
            initial_storage = self.initial_storage
            
        if initial_storage is None:
            raise ValueError("Initial storage must be provided")
        
        # Ensure data arrays are correct length
        if len(inflow_data) < forecast_periods:
            raise ValueError("Insufficient inflow data for forecast period")
        if len(demand_data) < forecast_periods:
            raise ValueError("Insufficient demand data for forecast period")
        
        # Initialize results
        dates = pd.date_range(
            start=pd.Timestamp.now().replace(day=1),
            periods=forecast_periods,
            freq='MS'
        )
        
        storage_levels = []
        inflows = []
        demands = []
        losses_list = []
        risk_status = []
        
        current_storage = initial_storage
        
        for i in range(forecast_periods):
            inflow = inflow_data[i]
            demand = demand_data[i]
            
            # Calculate losses
            loss_volume = current_storage * losses
            
            # Store current values
            storage_levels.append(current_storage)
            inflows.append(inflow)
            demands.append(demand)
            losses_list.append(loss_volume)
            
            # Calculate risk status
            risk = self._assess_risk(current_storage, demand, inflow)
            risk_status.append(risk)
            
            # Calculate next storage level
            current_storage = self.water_balance_model(
                current_storage, inflow, demand, losses
            )
        
        # Create results dataframe
        results_df = pd.DataFrame({
            'date': dates,
            'storage_level': storage_levels,
            'inflow': inflows,
            'demand': demands,
            'losses': losses_list,
            'risk_status': risk_status
        })
        
        self.simulation_results = results_df
        return results_df
    
    def _assess_risk(self, storage, demand, inflow):
        """
        Assess risk level based on storage conditions.
        
        Args:
            storage (float): Current storage level
            demand (float): Current demand
            inflow (float): Current inflow
            
        Returns:
            str: Risk status ('Safe', 'Moderate', 'Critical')
        """
        # Calculate storage as percentage of capacity (if known)
        if self.storage_capacity:
            storage_ratio = storage / self.storage_capacity
        else:
            # Use relative measures
            storage_ratio = storage / (storage + demand + 1)  # Add 1 to avoid division by zero
        
        # Risk assessment logic
        if storage_ratio > 0.6:  # More than 60% capacity
            return 'Safe'
        elif storage_ratio > 0.3:  # Between 30-60% capacity
            return 'Moderate'
        else:  # Below 30% capacity
            return 'Critical'
    
    def get_critical_periods(self):
        """
        Identify periods with critical storage levels.
        
        Returns:
            pd.DataFrame: Critical periods only
        """
        if self.simulation_results is None:
            raise ValueError("No simulation results available")
        
        critical_periods = self.simulation_results[
            self.simulation_results['risk_status'] == 'Critical'
        ]
        return critical_periods
    
    def get_summary_statistics(self):
        """
        Get summary statistics of simulation results.
        
        Returns:
            dict: Summary statistics
        """
        if self.simulation_results is None:
            raise ValueError("No simulation results available")
        
        df = self.simulation_results
        stats = {
            'total_periods': len(df),
            'safe_periods': len(df[df['risk_status'] == 'Safe']),
            'moderate_periods': len(df[df['risk_status'] == 'Moderate']),
            'critical_periods': len(df[df['risk_status'] == 'Critical']),
            'average_storage': df['storage_level'].mean(),
            'min_storage': df['storage_level'].min(),
            'max_storage': df['storage_level'].max(),
            'average_inflow': df['inflow'].mean(),
            'average_demand': df['demand'].mean()
        }
        
        return stats
    
    def set_storage_parameters(self, initial_storage, storage_capacity):
        """
        Set reservoir storage parameters.
        
        Args:
            initial_storage (float): Initial storage level
            storage_capacity (float): Maximum storage capacity
        """
        self.initial_storage = initial_storage
        self.storage_capacity = storage_capacity

def main():
    """Main function to demonstrate reservoir simulation."""
    # Sample data for demonstration
    np.random.seed(42)
    
    # Create sample forecast data (12 months)
    forecast_periods = 12
    dates = pd.date_range(
        start='2024-01-01',
        periods=forecast_periods,
        freq='MS'
    )
    
    # Sample inflow data (rainfall proxy)
    base_inflow = 150
    inflow_data = base_inflow + 50 * np.sin(2 * np.pi * np.arange(forecast_periods) / 12) + np.random.normal(0, 20, forecast_periods)
    inflow_data = np.maximum(inflow_data, 0)  # Ensure non-negative
    
    # Sample demand data (increasing trend)
    base_demand = 200
    demand_data = base_demand + np.linspace(0, 50, forecast_periods) + np.random.normal(0, 15, forecast_periods)
    demand_data = np.maximum(demand_data, 0)
    
    # Initialize simulator
    simulator = ReservoirSimulator(
        initial_storage=1000,  # Initial storage level
        storage_capacity=2000   # Maximum capacity
    )
    
    # Run simulation
    print("Running reservoir storage simulation...")
    results = simulator.simulate_storage(
        forecast_periods=forecast_periods,
        inflow_data=inflow_data,
        demand_data=demand_data,
        losses=0.05  # 5% losses
    )
    
    # Display results
    print("\nSimulation Results:")
    print(results[['date', 'storage_level', 'inflow', 'demand', 'risk_status']])
    
    # Summary statistics
    print("\nSummary Statistics:")
    stats = simulator.get_summary_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Critical periods
    critical = simulator.get_critical_periods()
    if len(critical) > 0:
        print(f"\nCritical periods detected: {len(critical)} months")
        print(critical[['date', 'storage_level', 'risk_status']])
    else:
        print("\nNo critical periods detected. All periods are safe or moderate risk.")

if __name__ == "__main__":
    main()