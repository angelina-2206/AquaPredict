"""
Data preprocessing module for AquaPredict system.
Handles loading, cleaning, and aggregating historical water data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class DataPreprocessor:
    """
    A class to preprocess water-related datasets for forecasting and analysis.
    """
    
    def __init__(self, data_dir='data'):
        """
        Initialize the DataPreprocessor.
        
        Args:
            data_dir (str): Directory containing raw data files
        """
        self.data_dir = data_dir
        self.processed_data = None
        
    def load_reservoir_data(self, file_path=None):
        """
        Load reservoir storage data.
        
        Args:
            file_path (str): Path to reservoir data file
            
        Returns:
            pd.DataFrame: Reservoir storage data
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'reservoir_storage.csv')
            
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            # Create sample data if file doesn't exist
            return self._create_sample_reservoir_data()
    
    def load_rainfall_data(self, file_path=None):
        """
        Load rainfall data.
        
        Args:
            file_path (str): Path to rainfall data file
            
        Returns:
            pd.DataFrame: Rainfall data
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'rainfall.csv')
            
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            return self._create_sample_rainfall_data()
    
    def load_consumption_data(self, file_path=None):
        """
        Load water consumption data.
        
        Args:
            file_path (str): Path to consumption data file
            
        Returns:
            pd.DataFrame: Water consumption data
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'water_consumption.csv')
            
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            return self._create_sample_consumption_data()
    
    def load_population_data(self, file_path=None):
        """
        Load population data.
        
        Args:
            file_path (str): Path to population data file
            
        Returns:
            pd.DataFrame: Population data
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'population.csv')
            
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            return self._create_sample_population_data()
    
    def clean_data(self, df, date_column='date'):
        """
        Clean data by handling missing values and ensuring proper data types.
        
        Args:
            df (pd.DataFrame): Input dataframe
            date_column (str): Name of date column
            
        Returns:
            pd.DataFrame: Cleaned dataframe
        """
        # Remove duplicates
        df = df.drop_duplicates(subset=[date_column])
        
        # Sort by date
        df = df.sort_values(by=date_column)
        
        # Handle missing values with forward fill
        df = df.fillna(method='ffill')
        
        # Remove any remaining NaN values
        df = df.dropna()
        
        return df
    
    def aggregate_monthly(self, df, date_column='date', value_column='value'):
        """
        Aggregate data to monthly level.
        
        Args:
            df (pd.DataFrame): Input dataframe
            date_column (str): Name of date column
            value_column (str): Name of value column to aggregate
            
        Returns:
            pd.DataFrame: Monthly aggregated data
        """
        df[date_column] = pd.to_datetime(df[date_column])
        df['year_month'] = df[date_column].dt.to_period('M')
        
        # Group by month and calculate mean
        monthly_df = df.groupby('year_month')[value_column].mean().reset_index()
        monthly_df['date'] = monthly_df['year_month'].dt.start_time
        monthly_df = monthly_df.drop('year_month', axis=1)
        
        return monthly_df
    
    def load_processed_data(self, filename='aquapredict_master_reservoir_dataset.csv'):
        """
        Load the regional master dataset.
        """
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            # Fallback to sample or previous processed if not found
            file_path = os.path.join(self.data_dir, 'processed_data.csv')
            
        df = pd.read_csv(file_path)
        # Handle variant date column names
        date_col = 'Date' if 'Date' in df.columns else 'date'
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Standardize column names for internal modules
        rename_map = {
            'Rainfall_mm': 'rainfall',
            'Total_Storage_BCM': 'storage',
            'Total_Capacity_BCM': 'capacity',
            'Percent_Full': 'percent_full',
            'Date': 'date',
            # New Master Dataset Columns
            'current_storage_mcm': 'storage',
            'capacity_mcm': 'capacity',
            'rainfall_mm': 'rainfall',
            'estimated_inflow_mcm': 'inflow',
            'water_demand_mcm': 'consumption',
            'state': 'State'
        }
        df = df.rename(columns=rename_map)
        
        # Sort and clean
        df = df.sort_values(['State', 'date']) if 'State' in df.columns else df.sort_values('date')
        
        # Synthesize inflow if missing (BCM scale)
        if 'rainfall' in df.columns and 'inflow' not in df.columns:
            # Conversion factor mm to BCM (approximate for large state catchments)
            df['inflow'] = df['rainfall'] * 0.05 
            
        # Ensure we have a consumption proxy if missing for forecasting
        if 'consumption' not in df.columns:
            # Proxy demand based on utilization trends (Percent_Full inverse)
            df['consumption'] = df['storage'].shift(1).fillna(df['storage']) + df['inflow'] - df['storage']
            df['consumption'] = df['consumption'].clip(lower=0)

        return df

    def get_states(self, df):
        """Get unique states in the dataset."""
        if 'State' in df.columns:
            return sorted(df['State'].unique())
        return ["Default"]

    def get_state_data(self, df, state_name):
        """Filter data for a specific state."""
        if 'State' in df.columns:
            return df[df['State'] == state_name].reset_index(drop=True)
        return df
    
    def save_processed_data(self, df, filename='processed_data.csv'):
        """
        Save processed data to CSV file.
        
        Args:
            df (pd.DataFrame): Processed dataframe
            filename (str): Output filename
        """
        output_path = os.path.join(self.data_dir, filename)
        df.to_csv(output_path, index=False)
        print(f"Processed data saved to {output_path}")
        

    
    def _create_sample_reservoir_data(self):
        """Create sample reservoir storage data for demonstration."""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        storage_values = 1000 + 200 * np.sin(2 * np.pi * np.arange(len(dates)) / 365) + np.random.normal(0, 50, len(dates))
        storage_values = np.maximum(storage_values, 0)  # Ensure non-negative
        
        df = pd.DataFrame({
            'date': dates,
            'storage': storage_values
        })
        return df
    
    def _create_sample_rainfall_data(self):
        """Create sample rainfall data for demonstration."""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        # Seasonal pattern with monsoon season
        rainfall_values = 10 + 15 * np.sin(2 * np.pi * np.arange(len(dates)) / 365 - np.pi/2) + np.random.exponential(5, len(dates))
        rainfall_values = np.maximum(rainfall_values, 0)
        
        df = pd.DataFrame({
            'date': dates,
            'rainfall': rainfall_values
        })
        return df
    
    def _create_sample_consumption_data(self):
        """Create sample water consumption data for demonstration."""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        # Increasing trend with seasonal variation
        trend = np.linspace(500, 800, len(dates))
        seasonal = 100 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
        noise = np.random.normal(0, 30, len(dates))
        consumption_values = trend + seasonal + noise
        consumption_values = np.maximum(consumption_values, 0)
        
        df = pd.DataFrame({
            'date': dates,
            'consumption': consumption_values
        })
        return df
    
    def _create_sample_population_data(self):
        """Create sample population data for demonstration."""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='MS')  # Monthly
        np.random.seed(42)
        # Steady population growth
        population_values = 100000 + np.linspace(0, 15000, len(dates)) + np.random.normal(0, 1000, len(dates))
        population_values = np.maximum(population_values, 0)
        
        df = pd.DataFrame({
            'date': dates,
            'population': population_values
        })
        return df

def main():
    """Main function to demonstrate preprocessing workflow."""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor('data')
    
    # Load datasets
    print("Loading datasets...")
    reservoir_df = preprocessor.load_reservoir_data()
    rainfall_df = preprocessor.load_rainfall_data()
    consumption_df = preprocessor.load_consumption_data()
    population_df = preprocessor.load_population_data()
    
    # Merge datasets
    print("Merging datasets...")
    master_df = preprocessor.merge_datasets(reservoir_df, rainfall_df, consumption_df, population_df)
    
    # Save processed data
    print("Saving processed data...")
    preprocessor.save_processed_data(master_df)
    
    print(f"Preprocessing complete. Processed data shape: {master_df.shape}")
    print("First few rows:")
    print(master_df.head())

if __name__ == "__main__":
    main()