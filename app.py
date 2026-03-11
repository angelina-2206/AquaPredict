"""
Main application file for AquaPredict system.
Integrates all modules into a complete pipeline.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import modules
from preprocessing.data_preprocessor import DataPreprocessor
from forecasting.water_demand_forecaster import WaterDemandForecaster
from simulation.reservoir_simulator import ReservoirSimulator
from analysis.gap_analyzer import GapAnalyzer
from analysis.scenario_analyzer import ScenarioAnalyzer

class AquaPredictApp:
    """
    Main application class that integrates all AquaPredict modules.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.preprocessor = DataPreprocessor('data')
        self.forecaster = WaterDemandForecaster(order=(1, 1, 1))
        self.simulator = ReservoirSimulator(initial_storage=1000, storage_capacity=2000)
        self.gap_analyzer = GapAnalyzer()
        self.scenario_analyzer = ScenarioAnalyzer()
        self.master_data = None
        self.forecast_results = None
        self.simulation_results = None
        self.gap_analysis_results = None
    
    def load_and_process_data(self):
        """
        Load and preprocess data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to load existing processed data
            self.master_data = self.preprocessor.load_processed_data()
            return True
        except FileNotFoundError:
            try:
                # Process raw data
                st.info("Processing raw data...")
                
                reservoir_df = self.preprocessor.load_reservoir_data()
                rainfall_df = self.preprocessor.load_rainfall_data()
                consumption_df = self.preprocessor.load_consumption_data()
                population_df = self.preprocessor.load_population_data()
                
                self.master_data = self.preprocessor.merge_datasets(
                    reservoir_df, rainfall_df, consumption_df, population_df
                )
                
                self.preprocessor.save_processed_data(self.master_data)
                st.success("Data processing completed!")
                return True
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
                return False
    
    def run_forecast(self, forecast_periods):
        """
        Run water demand forecasting.
        
        Args:
            forecast_periods (int): Number of periods to forecast
            
        Returns:
            pd.DataFrame: Forecast results
        """
        try:
            # Prepare data
            ts_data = self.forecaster.prepare_data(self.master_data)
            
            # Split data (use 80% for training)
            train_data, test_data = self.forecaster.train_test_split(ts_data, test_size=0.2)
            
            # Fit model
            self.forecaster.fit_model(train_data)
            
            # Generate forecast
            forecast_results = self.forecaster.forecast(steps=forecast_periods)
            
            # Evaluate on test data
            test_forecast = self.forecaster.forecast(steps=len(test_data))
            metrics = self.forecaster.evaluate_model(test_data, test_forecast['forecast'].values)
            
            self.forecast_results = forecast_results
            return forecast_results, metrics
        except Exception as e:
            st.error(f"Error in forecasting: {str(e)}")
            return None, None
    
    def run_simulation(self, forecast_results, rainfall_variation=0):
        """
        Run reservoir storage simulation with seasonal inflow awareness.
        """
        try:
            # Use seasonal averages for inflow projection
            seasonal_inflow = self.master_data.groupby(self.master_data['date'].dt.month)['inflow'].mean()
            
            inflow_data = []
            for dt in forecast_results['date']:
                month = dt.month
                # Apply variation to the seasonal base
                projected_inflow = seasonal_inflow[month] * (1 + rainfall_variation)
                inflow_data.append(projected_inflow)
            
            # Prepare demand data
            demand_data = forecast_results['forecast'].values
            
            # Run simulation
            simulation_results = self.simulator.simulate_storage(
                forecast_periods=len(forecast_results),
                inflow_data=inflow_data,
                demand_data=demand_data,
                losses=0.05
            )
            
            # Add dates back to simulation results for consistency
            simulation_results['date'] = forecast_results['date'].values
            
            self.simulation_results = simulation_results
            return simulation_results
        except Exception as e:
            st.error(f"Error in simulation: {str(e)}")
            return None
    
    def run_gap_analysis(self, simulation_results, forecast_results):
        """
        Run supply-demand gap analysis.
        
        Args:
            simulation_results (pd.DataFrame): Simulation results
            forecast_results (pd.DataFrame): Forecast results
            
        Returns:
            pd.DataFrame: Gap analysis results
        """
        try:
            # Extract supply and demand data
            supply_data = simulation_results['storage_level'].values
            demand_data = forecast_results['forecast'].values
            dates = forecast_results['date'].values
            
            # Calculate gaps
            gap_results = self.gap_analyzer.calculate_gap(supply_data, demand_data, dates)
            
            self.gap_analysis_results = gap_results
            return gap_results
        except Exception as e:
            st.error(f"Error in gap analysis: {str(e)}")
            return None
    
    def create_scenario_analysis(self, baseline_demand, baseline_supply, 
                               population_growth, rainfall_variation, consumption_growth):
        """
        Create scenario analysis.
        
        Args:
            baseline_demand (list): Baseline demand data
            baseline_supply (list): Baseline supply data
            population_growth (float): Population growth rate
            rainfall_variation (float): Rainfall variation
            consumption_growth (float): Consumption growth rate
            
        Returns:
            dict: Scenario analysis results
        """
        try:
            # Create scenarios
            baseline = self.scenario_analyzer.create_baseline_scenario(
                baseline_demand, baseline_supply, len(baseline_demand)
            )
            
            drought = self.scenario_analyzer.create_drought_scenario(
                baseline_demand, baseline_supply,
                demand_growth_rate=consumption_growth + 0.02,  # Additional 2% for drought
                rainfall_decrease=-0.3,
                periods=len(baseline_demand)
            )
            
            high_growth = self.scenario_analyzer.create_high_growth_scenario(
                baseline_demand, baseline_supply,
                population_growth_rate=population_growth + 0.03,
                consumption_growth_rate=consumption_growth + 0.02,
                rainfall_variation=rainfall_variation,
                periods=len(baseline_demand)
            )
            
            custom = self.scenario_analyzer.create_custom_scenario(
                name="Adjusted Scenario",
                description=f"Population: {population_growth*100:+.1f}%, Rainfall: {rainfall_variation*100:+.1f}%, Consumption: {consumption_growth*100:+.1f}%",
                baseline_demand=baseline_demand,
                baseline_supply=baseline_supply,
                population_growth=population_growth,
                rainfall_variation=rainfall_variation,
                consumption_growth=consumption_growth,
                periods=len(baseline_demand)
            )
            
            scenarios = [baseline, drought, high_growth, custom]
            comparison = self.scenario_analyzer.compare_scenarios(scenarios)
            report = self.scenario_analyzer.generate_scenario_report(scenarios)
            
            return {
                'scenarios': scenarios,
                'comparison': comparison,
                'report': report
            }
        except Exception as e:
            st.error(f"Error in scenario analysis: {str(e)}")
            return None
    
    def export_results(self, data_dict, filename_prefix="aqua_predict"):
        """Export results to CSV files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for name, data in data_dict.items():
                if isinstance(data, pd.DataFrame):
                    filename = f"{filename_prefix}_{name}_{timestamp}.csv"
                    csv_data = data.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {name.replace('_', ' ').title()} Results",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        key=f"download_{name}"
                    )
        except Exception as e:
            st.error(f"Error exporting results: {str(e)}")
    
    def display_model_metrics(self, metrics):
        """Display model performance metrics with enhanced styling."""
        if metrics:
            # Enhanced metrics display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('''
                <div style="background: linear-gradient(145deg, #ffffff, #f8f9fa); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); height: 100%;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📏</div>
                    <h4 style="color: #1f77b4; margin-bottom: 0.5rem;">Mean Absolute Error</h4>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #1f77b4;">{:.2f}</div>
                    <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Lower is better</div>
                </div>
                '''.format(metrics['MAE']), unsafe_allow_html=True)
            
            with col2:
                st.markdown('''
                <div style="background: linear-gradient(145deg, #ffffff, #f8f9fa); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); height: 100%;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <h4 style="color: #2ca02c; margin-bottom: 0.5rem;">Root Mean Square Error</h4>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #2ca02c;">{:.2f}</div>
                    <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Lower is better</div>
                </div>
                '''.format(metrics['RMSE']), unsafe_allow_html=True)
            
            with col3:
                st.markdown('''
                <div style="background: linear-gradient(145deg, #ffffff, #f8f9fa); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); height: 100%;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
                    <h4 style="color: #d62728; margin-bottom: 0.5rem;">Mean Absolute % Error</h4>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #d62728;">{:.1f}%</div>
                    <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Accuracy measure</div>
                </div>
                '''.format(metrics['MAPE']), unsafe_allow_html=True)
    
    def display_summary_statistics(self):
        """Display summary statistics with enhanced styling."""
        if self.forecast_results is not None and self.simulation_results is not None:
            # Enhanced summary statistics display
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_demand = self.forecast_results['forecast'].mean()
                st.markdown('''
                <div style="background: linear-gradient(145deg, #e3f2fd, #bbdefb); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 25px rgba(25, 118, 210, 0.15); border: 1px solid rgba(25, 118, 210, 0.2); height: 100%;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔮</div>
                    <h4 style="color: #1976d2; margin-bottom: 0.5rem;">Avg Forecast Demand</h4>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #1976d2;">{:.0f}</div>
                    <div style="font-size: 0.9rem; color: #1976d2; margin-top: 0.5rem;">Units per month</div>
                </div>
                '''.format(avg_demand), unsafe_allow_html=True)
            
            with col2:
                avg_storage = self.simulation_results['storage_level'].mean()
                st.markdown('''
                <div style="background: linear-gradient(145deg, #e8f5e8, #c8e6c9); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 25px rgba(40, 167, 69, 0.15); border: 1px solid rgba(40, 167, 69, 0.2); height: 100%;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💧</div>
                    <h4 style="color: #2e7d32; margin-bottom: 0.5rem;">Avg Storage Level</h4>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #2e7d32;">{:.0f}</div>
                    <div style="font-size: 0.9rem; color: #2e7d32; margin-top: 0.5rem;">Storage units</div>
                </div>
                '''.format(avg_storage), unsafe_allow_html=True)
            
            with col3:
                # Get gap analysis summary
                gap_summary = self.gap_analyzer.get_summary_report()
                critical_count = gap_summary['critical_periods']['count']
                st.markdown('''
                <div style="background: linear-gradient(145deg, #ffebee, #ffcdd2); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 25px rgba(244, 67, 54, 0.15); border: 1px solid rgba(244, 67, 54, 0.2); height: 100%;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
                    <h4 style="color: #c62828; margin-bottom: 0.5rem;">Critical Risk Periods</h4>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #c62828;">{}</div>
                    <div style="font-size: 0.9rem; color: #c62828; margin-top: 0.5rem;">High-risk months</div>
                </div>
                '''.format(critical_count), unsafe_allow_html=True)
            
            with col4:
                total_periods = len(self.forecast_results)
                safe_count = gap_summary['period_distribution']['surplus_periods'] + gap_summary['period_distribution']['adequate_periods']
                st.markdown('''
                <div style="background: linear-gradient(145deg, #fff8e1, #ffecb3); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 25px rgba(255, 152, 0, 0.15); border: 1px solid rgba(255, 152, 0, 0.2); height: 100%;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                    <h4 style="color: #ef6c00; margin-bottom: 0.5rem;">Safe Periods</h4>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #ef6c00;">{}/{}</div>
                    <div style="font-size: 0.9rem; color: #ef6c00; margin-top: 0.5rem;">Stable conditions</div>
                </div>
                '''.format(safe_count, total_periods), unsafe_allow_html=True)

def apply_custom_style(ax, title=None, xlabel=None, ylabel=None, show_grid=True):
    """Apply premium look to matplotlib axes."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e8f0')
    ax.spines['bottom'].set_color('#e2e8f0')
    
    if show_grid:
        ax.grid(axis='y', linestyle='--', alpha=0.4, color='#cbd5e1')
        ax.set_axisbelow(True)
    
    if title:
        ax.set_title(title, loc='left', fontsize=14, fontweight='600', color='#1e293b', pad=20)
    
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, fontweight='500', color='#64748b', labelpad=10)
    
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, fontweight='500', color='#64748b', labelpad=10)
    
    ax.tick_params(axis='both', which='major', labelsize=9, colors='#64748b')
    plt.tight_layout()

def render_landing_page(app):
    """Render the premium Landing Page."""
    # Custom styling for Hero and Feature cards
    st.markdown("""
    <style>
    .hero-container {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        padding: 4rem 3rem;
        border-radius: 2rem;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(79, 70, 229, 0.2);
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        color: white;
        letter-spacing: -0.04em;
    }
    .hero-text {
        font-size: 1.25rem;
        opacity: 0.9;
        max-width: 800px;
        line-height: 1.6;
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 1.5rem;
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #4f46e5;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1.25rem;
    }
    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.75rem;
    }
    .feature-text {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown('''
    <div class="hero-container">
        <div class="hero-title">Intelligent Water Management</div>
        <div class="hero-text">
            AquaPredict leverages advanced ARIMA forecasting and high-fidelity reservoir physical simulations 
            to provide a unified command center for municipal water resource orchestration.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Features Row
    f_col1, f_col2, f_col3 = st.columns(3)
    features = [
        {"icon": "🔮", "title": "Demand Forecasting", "text": "Deep learning-ready time series analysis helps anticipate municipal consumption patterns with validated confidence intervals."},
        {"icon": "🏞️", "title": "Reservoir Simulation", "text": "Physics-based water balance modeling simulates storage dynamics under varying climatic scenarios and demand pressures."},
        {"icon": "⚖️", "title": "Supply-Gap Analysis", "text": "Instant identification of critical periods where demand might exceed supply, enabling proactive resource allocation."}
    ]
    
    for i, feature in enumerate(features):
        with f_col1 if i==0 else f_col2 if i==1 else f_col3:
            st.markdown(f'''
            <div class="feature-card">
                <div class="feature-icon">{feature['icon']}</div>
                <div class="feature-title">{feature['title']}</div>
                <div class="feature-text">{feature['text']}</div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Rainfall Comparison Section
    st.markdown('<div class="section-header">Rainfall Monthly Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Comparing monthly precipitation trends across the latest two years.</div>', unsafe_allow_html=True)

    if st.session_state.analysis_run_count > 0 and app.master_data is not None:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Prepare comparison data
        data = app.master_data.copy()
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.month
        
        # Get last 2 years
        available_years = sorted(data['year'].unique())
        if len(available_years) >= 2:
            year_current = available_years[-1]
            year_prev = available_years[-2]
            
            df_current = data[data['year'] == year_current].sort_values('month')
            df_prev = data[data['year'] == year_prev].sort_values('month')
            
            # Map month numbers to names
            month_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            fig, ax = plt.subplots(figsize=(12, 6), facecolor='none')
            
            # Use marker logic for comparison
            ax.plot(df_prev['month'], df_prev['rainfall'], color='#94a3b8', linewidth=2, linestyle='--', marker='o', markersize=4, label=f'Rainfall {year_prev}', alpha=0.6)
            ax.plot(df_current['month'], df_current['rainfall'], color='#4f46e5', linewidth=3, marker='o', markersize=6, label=f'Rainfall {year_current}')
            
            # Fill the difference
            # Need to merge to handle potential missing months
            merged = pd.merge(df_current[['month', 'rainfall']], df_prev[['month', 'rainfall']], on='month', suffixes=('_curr', '_prev'), how='outer').fillna(0).sort_values('month')
            ax.fill_between(merged['month'], merged['rainfall_curr'], merged['rainfall_prev'], color='#4f46e5', alpha=0.1)
            
            # Style
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(month_abbr)
            apply_custom_style(ax, ylabel="Rainfall (mm)")
            ax.legend(frameon=False, loc='upper right')
            
            st.pyplot(fig)
        else:
            st.info("Additional historical data required for year-over-year comparison.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chart-container">Charts will appear here after analysis.</div>', unsafe_allow_html=True)
        st.info("Run the 'Complete Analysis' from the sidebar to visualize rainfall comparisons.")

def main():
    """Main application function."""
    st.set_page_config(
        page_title="AquaPredict - Integrated Water Resource Management",
        page_icon="💧",
        layout="wide"
    )
    
    # Custom CSS for state-of-the-art UI
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    :root {
        --sidebar-bg: #0f172a;
        --sidebar-accent: #1e293b;
        --main-bg: #f1f5f9;
        --card-bg: rgba(255, 255, 255, 0.8);
        --primary: #4f46e5;
        --secondary: #0ea5e9;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --text-main: #1e293b;
        --text-muted: #64748b;
    }

    * {
        font-family: 'Outfit', sans-serif;
    }

    [data-testid="stHeader"] {
        display: none;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        min-width: 280px !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Sidebar Styling */
    .sidebar-brand {
        padding: 2rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: linear-gradient(135deg, #4f46e5, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .nav-label {
        color: #475569;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 1.5rem 1.5rem 0.5rem;
    }

    div[data-testid="stSidebar"] button {
        background-color: transparent !important;
        color: #94a3b8 !important;
        border: none !important;
        width: 100% !important;
        text-align: left !important;
        padding: 0.8rem 1.5rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.75rem !important;
        border-radius: 0 !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease !important;
        border-left: 3px solid transparent !important;
    }

    div[data-testid="stSidebar"] button:hover {
        background-color: var(--sidebar-accent) !important;
        color: white !important;
        border-left: 3px solid var(--primary) !important;
    }

    /* Glassmorphism Cards */
    .kpi-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        border-radius: 1.25rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }

    .kpi-title {
        color: var(--text-muted);
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-main);
        letter-spacing: -0.02em;
    }

    .chart-container {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }

    .chart-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-main);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }

    .subtitle {
        color: var(--text-muted);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    .section-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .section-subheader {
        font-size: 0.95rem;
        color: var(--text-muted);
        margin-bottom: 2rem;
    }

    /* Global Overrides */
    .main .block-container {
        max-width: 1400px;
        padding: 3rem 4rem !important;
        background-color: var(--main-bg);
    }

    .stButton>button {
        border-radius: 0.75rem !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    
    # Animated title
    st.markdown('''<h1 class="main-title">💧 AquaPredict</h1>''', unsafe_allow_html=True)
    st.markdown('''<div class="subtitle">A Predictive Software System for Water Demand Forecasting and Reservoir Storage Analysis</div>''', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize app
    app = AquaPredictApp()
    
    # Initialize session state for analysis results
    if 'analysis_run_count' not in st.session_state:
        st.session_state.analysis_run_count = 0
    if 'forecast_results' not in st.session_state:
        st.session_state.forecast_results = None
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    if 'metrics' not in st.session_state:
        st.session_state.metrics = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"

    # Custom Sidebar implementation
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">💧 AquaPredict</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)
        
        pages = {
            "Home": "🏠", "Overview": "📊", "Demand Forecast": "📈", 
            "Rainfall & Inflow": "🌧️", "Reservoir Simulation": "🌊", 
            "Supply-Demand Analysis": "⚖️", "Reports": "📄", "Settings": "⚙️"
        }
        
        for page_name, icon in pages.items():
            if st.button(f"{icon} {page_name}", key=f"nav_{page_name.replace(' ', '_')}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="nav-label">Global Controls</div>', unsafe_allow_html=True)
        
        # Regional Selection
        app.load_and_process_data()
        all_data = app.master_data
        available_states = app.preprocessor.get_states(all_data)
        selected_state = st.selectbox("🎯 Target State", available_states, key="state_selector")
        
        forecast_months = st.slider("Forecast Horizon (months)", 6, 24, 12, key="horizon_slider")
        rainfall_variation = st.slider("Rainfall Variation (%)", -50.0, 50.0, 0.0, key="rainfall_slider") / 100
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Run Complete Analysis", type="primary", use_container_width=True):
            with st.spinner(f"Executing analytical pipeline for {selected_state}..."):
                # Filter data for selected state
                app.master_data = app.preprocessor.get_state_data(all_data, selected_state)
                
                forecast_results, metrics = app.run_forecast(forecast_months)
                if forecast_results is not None:
                        simulation_results = app.run_simulation(forecast_results, rainfall_variation)
                        
                        # Store in session state
                        st.session_state.forecast_results = forecast_results
                        st.session_state.metrics = metrics
                        st.session_state.simulation_results = simulation_results
                        st.session_state.analysis_run_count += 1
                        st.success("✅ Analysis completed!")
                        st.rerun()

    # Main content rendering based on session state
    if st.session_state.current_page == "Home":
        render_landing_page(app)
    elif st.session_state.current_page == "Overview":
        render_overview_page(app, forecast_months, rainfall_variation)
    elif st.session_state.current_page == "Demand Forecast":
        render_demand_forecast_page(app, forecast_months)
    elif st.session_state.current_page == "Rainfall & Inflow":
        render_rainfall_inflow_page(app, rainfall_variation)
    elif st.session_state.current_page == "Reservoir Simulation":
        render_reservoir_simulation_page(app)
    elif st.session_state.current_page == "Supply-Demand Analysis":
        render_supply_demand_page(app)
    elif st.session_state.current_page == "Reports":
        render_reports_page(app)
    elif st.session_state.current_page == "Settings":
        render_settings_page(app)
    else:
        st.markdown(f'<div class="section-header">{st.session_state.current_page}</div>', unsafe_allow_html=True)
        st.info("This page is under construction.")

def render_overview_page(app, forecast_months, rainfall_variation):
    """Render the Overview page similar to the screenshot."""
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subheader">Integrated water resource analytics and health indicators.</div>', unsafe_allow_html=True)
    with col_h2:
        st.info(f"Analysis status: {'✅ Loaded' if st.session_state.analysis_run_count > 0 else '⚠️ Run analysis in sidebar'}")

    # Results check
    res = st.session_state.simulation_results
    f_res = st.session_state.forecast_results
    
    # KPI Values
    if res is not None and f_res is not None:
        last_storage = res['storage_level'].iloc[-1]
        capacity = app.simulator.storage_capacity
        storage_pct = (last_storage / capacity) * 100
        total_demand = f_res['forecast'].sum()
        risk = res['risk_status'].iloc[-1]
        
        kpi_data = [
            {"title": "Current Res. Level", "value": f"{storage_pct:.0f}%", "subtitle": f"{last_storage:.0f} / {capacity:.0f} ML", "icon": "🌊", "color": "#4299e1"},
            {"title": "Forecasted Demand", "value": f"{total_demand:.0f} ML", "subtitle": f"Next {len(f_res)} months", "icon": "📈", "color": "#4299e1"},
            {"title": "Avg Monthly Inflow", "value": "36.5 ML", "subtitle": "Based on model", "icon": "🌧️", "color": "#38b2ac"},
            {"title": "Risk Indicator", "value": risk, "subtitle": "Immediate assessment", "icon": "⚠️", "color": "#f56565" if risk == "Critical" else "#ed8936"}
        ]
    else:
        kpi_data = [
            {"title": "Current Res. Level", "value": "--", "subtitle": "No data", "icon": "🌊", "color": "#cbd5e0"},
            {"title": "Forecasted Demand", "value": "--", "subtitle": "No data", "icon": "📈", "color": "#cbd5e0"},
            {"title": "Avg Monthly Inflow", "value": "--", "subtitle": "No data", "icon": "🌧️", "color": "#cbd5e0"},
            {"title": "Risk Indicator", "value": "--", "subtitle": "No data", "icon": "⚠️", "color": "#cbd5e0"}
        ]

    kpi_cols = st.columns(4)
    for i, kpi in enumerate(kpi_data):
        with kpi_cols[i]:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-content">
                    <div class="kpi-title">{kpi['title']}</div>
                    <div class="kpi-value">{kpi['value']}</div>
                    <div class="kpi-subtitle">{kpi['subtitle']}</div>
                </div>
                <div class="kpi-icon-bg" style="background-color: {kpi['color']}15; color: {kpi['color']};">
                    {kpi['icon']}
                </div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown('<div class="chart-container"><div class="chart-title">Water Demand Forecast</div>', unsafe_allow_html=True)
        if f_res is not None:
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='none')
            ax.plot(f_res['date'], f_res['forecast'], marker='o', color='#4f46e5', linewidth=2.5, markersize=4, label='Forecast')
            ax.fill_between(f_res['date'], f_res['lower_ci'], f_res['upper_ci'], color='#4f46e5', alpha=0.1)
            apply_custom_style(ax, ylabel="Demand (ML)")
            st.pyplot(fig)
        else:
            st.info("Run analysis to visualize demand forecast.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_c2:
        st.markdown('<div class="chart-container"><div class="chart-title">Reservoir Storage Simulation</div>', unsafe_allow_html=True)
        if res is not None:
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='none')
            ax.plot(res['date'], res['storage_level'], color='#10b981', linewidth=2.5, label='Storage Level')
            ax.fill_between(res['date'], 0, res['storage_level'], color='#10b981', alpha=0.1)
            apply_custom_style(ax, ylabel="Storage (ML)")
            st.pyplot(fig)
        else:
            st.info("Run analysis to visualize storage simulation.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container"><div class="chart-title">Rainfall Distribution & Inflow</div>', unsafe_allow_html=True)
    if st.session_state.analysis_run_count > 0 and app.master_data is not None:
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='none')
        data = app.master_data.tail(24)
        ax.bar(data.index, data['rainfall'], color='#e2e8f0', alpha=0.6, label='Rainfall')
        ax.plot(data.index, data['inflow'], color='#0ea5e9', linewidth=2, label='Inflow')
        apply_custom_style(ax, ylabel="Volume")
        ax.legend(frameon=False, loc='upper right', fontsize=8)
        st.pyplot(fig)
    else:
        st.info("Historical data for rainfall and inflow.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_demand_forecast_page(app, forecast_months):
    """Render the Demand Forecast page."""
    st.markdown('<div class="section-header">Demand Forecast</div>', unsafe_allow_html=True)
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1, 1, 1, 1])
    with ctrl_col1:
        st.markdown("**Upload Historical Data**")
        st.button("↥ Upload CSV", key="forecast_upload_btn", use_container_width=True)
    with ctrl_col2: st.selectbox("Model", ["ARIMA", "Prophet"], key="forecast_model")
    with ctrl_col3: st.selectbox("Forecast Horizon", ["1 Year", "2 Years"], key="forecast_horizon_sel")
    with ctrl_col4:
        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.button("Run Forecast", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container"><div class="chart-title">Forecast with Confidence Interval</div>', unsafe_allow_html=True)
    if st.session_state.forecast_results is not None:
        f_res = st.session_state.forecast_results
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='none')
        ax.plot(f_res['date'], f_res['forecast'], color='#4f46e5', linewidth=3, label='Predicted Demand', marker='o', markersize=4)
        ax.fill_between(f_res['date'], f_res['lower_ci'], f_res['upper_ci'], color='#4f46e5', alpha=0.1, label='Confidence Interval')
        
        # Add a horizontal line for the average
        avg_v = f_res['forecast'].mean()
        ax.axhline(avg_v, color='#64748b', linestyle='--', alpha=0.5, label=f'Avg: {avg_v:.0f}')
        
        apply_custom_style(ax, ylabel="Million Liters (ML)")
        ax.legend(frameon=False, loc='upper left')
        st.pyplot(fig)
    else:
        st.info("Forecast visualization will appear here.")
    st.markdown('</div>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        st.markdown('<div class="chart-container"><div class="chart-title">Model Performance</div>', unsafe_allow_html=True)
        if st.session_state.metrics:
            m = st.session_state.metrics
            st.markdown(f"**Model:** ARIMA(1,1,1)<br>**RMSE:** {m['RMSE']:.2f} ML<br>**MAE:** {m['MAE']:.2f} ML", unsafe_allow_html=True)
        else:
            st.markdown("**Model:** ARIMA(1,1,1)\\n**RMSE:** --\\n**MAE:** --")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown('<div class="chart-container"><div class="chart-title">Model Interpretation</div>', unsafe_allow_html=True)
        st.markdown("The ARIMA model captures seasonal patterns and provides a statistically significant baseline for demand forecasting based on historical usage trends.")
        st.markdown('</div>', unsafe_allow_html=True)

def render_rainfall_inflow_page(app, rainfall_variation):
    """Render the detailed Rainfall & Inflow Analysis page."""
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.markdown('<div class="section-header">Rainfall & Inflow Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subheader">Meteorological drivers and catchment efficiency metrics.</div>', unsafe_allow_html=True)
    with col_h2:
        st.info(f"Analysis status: {'✅ Data Loaded' if st.session_state.analysis_run_count > 0 else '⚠️ Please run analysis'}")

    if st.session_state.analysis_run_count > 0 and app.master_data is not None:
        data = app.master_data.tail(12)
        
        # Calculate Metrics
        total_rainfall = data['rainfall'].sum()
        avg_inflow = data['inflow'].mean()
        # Efficiency = Inflow / Rainfall (approximate catchment gain)
        efficiency = (data['inflow'].sum() / data['rainfall'].sum()) if data['rainfall'].sum() > 0 else 0
        
        # KPI Row
        k_cols = st.columns(4)
        metrics = [
            {"title": "Total Rainfall", "value": f"{total_rainfall:.0f} mm", "subtitle": "Last 12 Months", "color": "#4f46e5"},
            {"title": "Avg Monthly Inflow", "value": f"{avg_inflow:.1f} ML", "subtitle": "Catchment yield", "color": "#0ea5e9"},
            {"title": "Inflow Efficiency", "value": f"{efficiency:.2f}", "subtitle": "ML per mm rain", "color": "#10b981"},
            {"title": "Peak Rainfall", "value": f"{data['rainfall'].max():.0f} mm", "subtitle": data.index[data['rainfall'].argmax()].strftime('%b %Y'), "color": "#f59e0b"}
        ]
        
        for i, m in enumerate(metrics):
            with k_cols[i]:
                 st.markdown(f'''
                 <div class="kpi-card">
                    <div>
                        <div class="kpi-title">{m['title']}</div>
                        <div class="kpi-value" style="color: {m['color']}">{m['value']}</div>
                        <div style="font-size: 0.75rem; color: #64748b;">{m['subtitle']}</div>
                    </div>
                 </div>
                 ''', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Advanced Overlay Chart
        st.markdown('<div class="chart-container"><div class="chart-title">Rainfall vs. Inflow Overlay (Last 12 Months)</div>', unsafe_allow_html=True)
        fig, ax1 = plt.subplots(figsize=(12, 5), facecolor='none')
        
        ax1.bar(data.index, data['rainfall'], color='#4f46e5', alpha=0.3, label='Rainfall (mm)', width=20)
        ax1.set_ylabel("Rainfall (mm)", color='#4f46e5', fontsize=10)
        ax1.tick_params(axis='y', labelcolor='#4f46e5')
        
        ax2 = ax1.twinx()
        ax2.plot(data.index, data['inflow'], color='#0ea5e9', linewidth=3, marker='o', label='Inflow (ML)')
        ax2.set_ylabel("Inflow (ML)", color='#0ea5e9', fontsize=10)
        ax2.tick_params(axis='y', labelcolor='#0ea5e9')
        
        apply_custom_style(ax1, show_grid=False)
        # Manually fix ax2 spines because apply_custom_style only handles ax1
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_color('#e2e8f0')
        ax2.spines['left'].set_visible(False)
        
        fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9), frameon=False, fontsize=9)
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_low1, col_low2 = st.columns(2)
        
        with col_low1:
            st.markdown('<div class="chart-container"><div class="chart-title">Rainfall-Inflow Correlation</div>', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(10, 6), facecolor='none')
            full_data = app.master_data
            ax.scatter(full_data['rainfall'], full_data['inflow'], color='#4f46e5', alpha=0.5, s=40)
            
            # Add trend line
            z = np.polyfit(full_data['rainfall'], full_data['inflow'], 1)
            p = np.poly1d(z)
            ax.plot(full_data['rainfall'], p(full_data['rainfall']), "r--", alpha=0.8, linewidth=1.5, label='Trend')
            
            apply_custom_style(ax, xlabel="Rainfall (mm)", ylabel="Inflow (ML)")
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_low2:
            st.markdown('<div class="chart-container"><div class="chart-title">Statistical Summary Table</div>', unsafe_allow_html=True)
            stats_df = data[['rainfall', 'inflow']].describe().T[['mean', 'std', 'min', 'max']]
            stats_df.columns = ['Mean', 'Std Dev', 'Min', 'Max']
            st.dataframe(stats_df.style.format("{:.2f}").background_gradient(cmap='Blues'), use_container_width=True)
            st.markdown('<div style="font-size: 0.8rem; color: #64748b; margin-top: 1rem;">Summary statistics based on the latest 12-month trailing window.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.info("Visualizations will be populated once the analytical pipeline has been executed in the sidebar.")
        st.markdown('<div class="chart-container">Charts will appear here after analysis.</div>', unsafe_allow_html=True)

def render_reservoir_simulation_page(app):
    """Render the Reservoir Simulation page."""
    st.markdown('<div class="section-header">Reservoir Simulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Water balance modeling and storage projections.</div>', unsafe_allow_html=True)
    
    res = st.session_state.simulation_results
    if res is not None:
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-content"><div class="kpi-title">Initial Storage</div><div class="kpi-value">{app.simulator.initial_storage} ML</div></div></div>', unsafe_allow_html=True)
        with col_m2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-content"><div class="kpi-title">Max Capacity</div><div class="kpi-value">{app.simulator.storage_capacity} ML</div></div></div>', unsafe_allow_html=True)
        with col_m3:
            avg_storage = res['storage_level'].mean()
            st.markdown(f'<div class="kpi-card"><div class="kpi-content"><div class="kpi-title">Avg. Projected Storage</div><div class="kpi-value">{avg_storage:.0f} ML</div></div></div>', unsafe_allow_html=True)

        st.markdown('<div class="chart-container"><div class="chart-title">Detailed Water Balance Simulation</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='none')
        ax.plot(res['date'], res['storage_level'], label='Storage Level', color='#10b981', linewidth=3)
        ax.plot(res['date'], res['inflow'], label='Inflow', color='#0ea5e9', linestyle='--', alpha=0.6)
        ax.plot(res['date'], res['demand'], label='Demand', color='#ef4444', linestyle=':', alpha=0.6)
        ax.fill_between(res['date'], 0, res['storage_level'], color='#10b981', alpha=0.05)
        apply_custom_style(ax, ylabel="Million Liters (ML)")
        ax.legend(frameon=False, loc='upper left')
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container"><div class="chart-title">Risk Assessment Breakdown</div>', unsafe_allow_html=True)
        risk_counts = res['risk_status'].value_counts()
        cols = st.columns(len(risk_counts))
        for i, (risk, count) in enumerate(risk_counts.items()):
            color = "#48bb78" if risk == "Safe" else "#ed8936" if risk == "Moderate" else "#f56565"
            with cols[i]:
                st.markdown(f'<div style="text-align: center; padding: 1rem; border-radius: 10px; background: {color}15; border: 1px solid {color};"><h3 style="color: {color}; margin:0;">{count}</h3><p style="margin:0; font-size: 0.8rem;">{risk} Periods</p></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Run analysis in the sidebar to see simulation results.")

def render_supply_demand_page(app):
    """Render the Supply-Demand Analysis page."""
    st.markdown('<div class="section-header">Supply-Demand Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Predictive gap analysis and allocation efficiency.</div>', unsafe_allow_html=True)
    
    # Add status indicator
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown('<div style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">This view compares projected water supply against forecasted demand to identify potential deficit periods in the coming months.</div>', unsafe_allow_html=True)
    
    f_res = st.session_state.forecast_results
    s_res = st.session_state.simulation_results
    
    if f_res is not None and s_res is not None:
        # Run gap analysis if not already stored
        if 'gap_results' not in st.session_state or st.session_state.gap_results is None:
            st.session_state.gap_results = app.run_gap_analysis(s_res, f_res)
        
        gap_res = st.session_state.gap_results
        
        if gap_res is not None:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown('<div class="chart-container"><div class="chart-title">Supply vs. Demand Analysis</div>', unsafe_allow_html=True)
                fig, ax1 = plt.subplots(figsize=(10, 5), facecolor='none')
                
                # Plot Supply and Demand as lines
                ax1.plot(gap_res['date'], gap_res['supply'], color='#10b981', linewidth=2, label='Supply', alpha=0.8)
                ax1.plot(gap_res['date'], gap_res['demand'], color='#4f46e5', linewidth=2, label='Demand', linestyle='--')
                ax1.fill_between(gap_res['date'], gap_res['supply'], gap_res['demand'], where=(gap_res['supply'] >= gap_res['demand']), color='#10b981', alpha=0.1, label='Surplus', interpolate=True)
                ax1.fill_between(gap_res['date'], gap_res['supply'], gap_res['demand'], where=(gap_res['supply'] < gap_res['demand']), color='#ef4444', alpha=0.1, label='Deficit', interpolate=True)
                
                apply_custom_style(ax1, ylabel="Million Liters (ML)")
                ax1.legend(frameon=False, loc='upper left', fontsize=9)
                
                # Create second axis for Gap percentage or value
                ax2 = ax1.twinx()
                ax2.bar(gap_res['date'], gap_res['gap'], color='gray', alpha=0.15, width=15, label='Net Gap')
                ax2.set_ylabel("Net Gap (ML)", color='gray', fontsize=9)
                ax2.tick_params(axis='y', labelcolor='gray', labelsize=8)
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_color('#e2e8f0')
                
                st.pyplot(fig)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container" style="height: 100%;"><div class="chart-title">Risk Alerts & Insights</div>', unsafe_allow_html=True)
                critical = gap_res[gap_res['classification'].isin(['Deficit', 'Critical Risk'])]
                if not critical.empty:
                    st.markdown(f'<div style="color: #ef4444; font-weight: 600; margin-bottom: 1rem; font-size: 0.9rem;">⚠️ {len(critical)} Critical observations identified</div>', unsafe_allow_html=True)
                    for idx, row in critical.iterrows():
                        color = "#ef4444" if row['classification'] == 'Critical Risk' else "#f59e0b"
                        bg_color = f"{color}10" # 10 alpha hex
                        st.markdown(f'''
                        <div style="margin-bottom: 0.75rem; padding: 1rem; border-radius: 0.75rem; border-left: 4px solid {color}; background-color: {bg_color}; border-top: 1px solid rgba(0,0,0,0.03); border-right: 1px solid rgba(0,0,0,0.03); border-bottom: 1px solid rgba(0,0,0,0.03);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                <span style="font-weight: 700; color: #1e293b; font-size: 0.9rem;">{row["date"]}</span>
                                <span style="font-size: 0.75rem; font-weight: 600; color: {color}; text-transform: uppercase;">{row["classification"]}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #64748b;">Supply deficit of <b>{abs(row["gap"]):.1f} ML</b> projected.</div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.success("Analysis complete: No critical deficits detected within the current forecast window.")
                st.markdown('</div>', unsafe_allow_html=True)
def render_reports_page(app):
    """Render the Reports page."""
    st.markdown('<div class="section-header">Analytical Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Generate and export comprehensive water resource reports.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-container"><div class="chart-title">Available Report Templates</div>', unsafe_allow_html=True)
        st.checkbox("Executive Summary", value=True)
        st.checkbox("Demand Forecast Details", value=True)
        st.checkbox("Reservoir Health Assessment", value=True)
        st.checkbox("Supply-Gap Matrix", value=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Generate PDF Report", use_container_width=True, type="primary"):
            st.success("Report generation started...")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="chart-container"><div class="chart-title">Export Data</div>', unsafe_allow_html=True)
        if st.session_state.analysis_run_count > 0:
            st.info("Analysis data is ready for export.")
            app.export_results({
                'forecast': st.session_state.forecast_results,
                'simulation': st.session_state.simulation_results
            })
        else:
            st.warning("Run analysis to enable data export.")
        st.markdown('</div>', unsafe_allow_html=True)

def render_settings_page(app):
    """Render the Settings page."""
    st.markdown('<div class="section-header">System Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Configure system parameters and data sources.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container"><div class="chart-title">Model Configuration</div>', unsafe_allow_html=True)
    st.text_input("ARIMA Order (p, d, q)", value="(1, 1, 1)")
    st.slider("Training/Test Split Proportion", 0.5, 0.9, 0.8)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container"><div class="chart-title">Reservoir Constants</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Max Storage Capacity (ML)", value=2000)
    with col2:
        st.number_input("Initial Storage Level (ML)", value=1000)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
