"""
Water demand forecasting engine using ARIMA models.
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class WaterDemandForecaster:
    """
    A class to forecast water demand using ARIMA time series modeling.
    """
    
    def __init__(self, order=(1, 1, 1)):
        """
        Initialize the forecaster with ARIMA parameters.
        
        Args:
            order (tuple): ARIMA(p,d,q) order parameters
        """
        self.order = order
        self.model = None
        self.fitted_model = None
        self.train_data = None
        self.test_data = None
        self.forecast_results = None
        self.metrics = None
    
    def prepare_data(self, df, target_column='consumption', date_column='date'):
        """
        Prepare data for forecasting.
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Column to forecast
            date_column (str): Date column name
            
        Returns:
            pd.Series: Time series data indexed by date
        """
        # Set date as index
        ts_data = df.set_index(date_column)[target_column]
        return ts_data
    
    def train_test_split(self, ts_data, test_size=0.2):
        """
        Split time series data into train and test sets.
        
        Args:
            ts_data (pd.Series): Time series data
            test_size (float): Proportion of data for testing
            
        Returns:
            tuple: (train_data, test_data)
        """
        split_index = int(len(ts_data) * (1 - test_size))
        train_data = ts_data[:split_index]
        test_data = ts_data[split_index:]
        
        self.train_data = train_data
        self.test_data = test_data
        
        return train_data, test_data
    
    def fit_model(self, train_data):
        """
        Fit ARIMA model to training data.
        
        Args:
            train_data (pd.Series): Training time series data
            
        Returns:
            ARIMAResults: Fitted model
        """
        self.model = ARIMA(train_data, order=self.order)
        self.fitted_model = self.model.fit()
        return self.fitted_model
    
    def forecast(self, steps, exog=None):
        """
        Generate forecasts for specified number of steps.
        
        Args:
            steps (int): Number of periods to forecast
            exog (pd.DataFrame): Exogenous variables (optional)
            
        Returns:
            pd.DataFrame: Forecast results with confidence intervals
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before forecasting")
        
        # Generate forecast
        forecast_result = self.fitted_model.forecast(steps=steps)
        
        # Get confidence intervals
        forecast_ci = self.fitted_model.get_forecast(steps=steps)
        conf_int = forecast_ci.conf_int()
        
        # Create results dataframe
        forecast_dates = pd.date_range(
            start=self.train_data.index[-1] + pd.DateOffset(months=1),
            periods=steps,
            freq='MS'
        )
        
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast_result.values,
            'lower_ci': conf_int.iloc[:, 0].values,
            'upper_ci': conf_int.iloc[:, 1].values
        })
        
        self.forecast_results = forecast_df
        return forecast_df
    
    def evaluate_model(self, test_data, forecast_values):
        """
        Evaluate model performance using test data.
        
        Args:
            test_data (pd.Series): Actual test values
            forecast_values (array): Predicted values
            
        Returns:
            dict: Performance metrics
        """
        # Align lengths if needed
        min_length = min(len(test_data), len(forecast_values))
        actual = test_data.iloc[:min_length]
        predicted = forecast_values[:min_length]
        
        # Calculate metrics
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        
        self.metrics = {
            'MAE': mae,
            'RMSE': rmse,
            'MAPE': mape
        }
        
        return self.metrics
    
    def get_model_summary(self):
        """
        Get detailed model summary.
        
        Returns:
            str: Model summary information
        """
        if self.fitted_model is None:
            return "No model fitted yet"
        
        return self.fitted_model.summary()
    
    def auto_optimize_order(self, train_data, max_p=3, max_d=2, max_q=3):
        """
        Automatically find optimal ARIMA parameters using AIC.
        
        Args:
            train_data (pd.Series): Training data
            max_p (int): Maximum AR order
            max_d (int): Maximum differencing order
            max_q (int): Maximum MA order
            
        Returns:
            tuple: Optimal (p,d,q) order
        """
        best_aic = np.inf
        best_order = None
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(train_data, order=(p, d, q))
                        fitted_model = model.fit()
                        aic = fitted_model.aic
                        
                        if aic < best_aic:
                            best_aic = aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        self.order = best_order
        print(f"Optimal ARIMA order: {best_order} (AIC: {best_aic:.2f})")
        return best_order

def main():
    """Main function to demonstrate forecasting workflow."""
    # Import preprocessor
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from preprocessing.data_preprocessor import DataPreprocessor
    
    # Load processed data
    preprocessor = DataPreprocessor('../data')
    try:
        master_df = preprocessor.load_processed_data()
    except FileNotFoundError:
        print("Processed data not found. Running preprocessing first...")
        preprocessor = DataPreprocessor('data')
        reservoir_df = preprocessor.load_reservoir_data()
        rainfall_df = preprocessor.load_rainfall_data()
        consumption_df = preprocessor.load_consumption_data()
        population_df = preprocessor.load_population_data()
        master_df = preprocessor.merge_datasets(reservoir_df, rainfall_df, consumption_df, population_df)
        preprocessor.save_processed_data(master_df)
    
    # Initialize forecaster
    forecaster = WaterDemandForecaster(order=(1, 1, 1))
    
    # Prepare data
    ts_data = forecaster.prepare_data(master_df)
    print(f"Time series data shape: {ts_data.shape}")
    
    # Split data
    train_data, test_data = forecaster.train_test_split(ts_data, test_size=0.2)
    print(f"Train data: {len(train_data)} months")
    print(f"Test data: {len(test_data)} months")
    
    # Fit model
    print("Fitting ARIMA model...")
    fitted_model = forecaster.fit_model(train_data)
    print("Model fitted successfully")
    
    # Generate forecasts for test period
    forecast_steps = len(test_data)
    forecast_df = forecaster.forecast(steps=forecast_steps)
    
    # Evaluate model
    metrics = forecaster.evaluate_model(test_data, forecast_df['forecast'].values)
    print("\nModel Performance Metrics:")
    print(f"MAE: {metrics['MAE']:.2f}")
    print(f"RMSE: {metrics['RMSE']:.2f}")
    print(f"MAPE: {metrics['MAPE']:.2f}%")
    
    # Forecast future demand (next 12 months)
    print("\nForecasting next 12 months...")
    future_forecast = forecaster.forecast(steps=12)
    print("Future demand forecast:")
    print(future_forecast[['date', 'forecast']].head(12))

if __name__ == "__main__":
    main()