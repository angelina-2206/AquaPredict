"""
Dashboard module for AquaPredict system.
Streamlit interface with matplotlib visualizations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io

# Set matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')

class AquaPredictDashboard:
    """
    Streamlit dashboard for AquaPredict system.
    """
    
    def __init__(self):
        """Initialize dashboard components."""
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="AquaPredict - Water Demand Forecasting",
            page_icon="💧",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def setup_sidebar(self):
        """Setup sidebar controls."""
        st.sidebar.title("🔮 AquaPredict Controls")
        
        # Forecast parameters
        st.sidebar.subheader("Forecast Settings")
        forecast_months = st.sidebar.slider(
            "Forecast Horizon (months)",
            min_value=6,
            max_value=24,
            value=12,
            step=1
        )
        
        # Scenario parameters
        st.sidebar.subheader("Scenario Adjustments")
        population_growth = st.sidebar.slider(
            "Population Growth (%)",
            min_value=-5.0,
            max_value=10.0,
            value=2.0,
            step=0.5
        ) / 100
        
        rainfall_variation = st.sidebar.slider(
            "Rainfall Variation (%)",
            min_value=-50.0,
            max_value=50.0,
            value=0.0,
            step=5.0
        ) / 100
        
        consumption_growth = st.sidebar.slider(
            "Consumption Growth (%)",
            min_value=-10.0,
            max_value=15.0,
            value=3.0,
            step=0.5
        ) / 100
        
        # Run simulation button
        run_simulation = st.sidebar.button("📊 Run Simulation", type="primary")
        
        return {
            'forecast_months': forecast_months,
            'population_growth': population_growth,
            'rainfall_variation': rainfall_variation,
            'consumption_growth': consumption_growth,
            'run_simulation': run_simulation
        }
    
    def create_header(self):
        """Create dashboard header."""
        st.title("💧 AquaPredict")
        st.markdown("""
        **A Predictive Software System for Water Demand Forecasting and Reservoir Storage Analysis**
        
        Forecast water demand, simulate reservoir storage, and analyze supply-demand gaps under various scenarios.
        """)
        st.markdown("---")
    
    def create_demand_forecast_chart(self, dates, actual_demand, forecast_demand, lower_ci=None, upper_ci=None):
        """
        Create demand forecast visualization.
        
        Args:
            dates: Date range for visualization
            actual_demand: Historical demand data
            forecast_demand: Forecasted demand data
            lower_ci: Lower confidence interval
            upper_ci: Upper confidence interval
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot historical data
        historical_dates = dates[:len(actual_demand)]
        ax.plot(historical_dates, actual_demand, 'b-', linewidth=2, label='Historical Demand', marker='o')
        
        # Plot forecast
        forecast_dates = dates[len(actual_demand):len(actual_demand) + len(forecast_demand)]
        ax.plot(forecast_dates, forecast_demand, 'r--', linewidth=2, label='Forecasted Demand', marker='s')
        
        # Plot confidence intervals if provided
        if lower_ci is not None and upper_ci is not None:
            ax.fill_between(forecast_dates, lower_ci, upper_ci, alpha=0.3, color='red', label='Confidence Interval')
        
        # Formatting
        ax.set_title('Water Demand Forecast', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Water Demand (Units)', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Date formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_reservoir_storage_chart(self, dates, storage_levels, risk_status):
        """
        Create reservoir storage visualization.
        
        Args:
            dates: Date range
            storage_levels: Storage level data
            risk_status: Risk classification for each period
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create color mapping for risk levels
        colors = []
        for status in risk_status:
            if status == 'Safe':
                colors.append('green')
            elif status == 'Moderate':
                colors.append('orange')
            else:  # Critical
                colors.append('red')
        
        # Plot storage levels
        bars = ax.bar(dates, storage_levels, color=colors, alpha=0.7)
        
        # Add risk level indicators
        for i, (bar, status) in enumerate(zip(bars, risk_status)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   status, ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # Formatting
        ax.set_title('Reservoir Storage Simulation', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Storage Level (Units)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Date formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, label='Safe'),
            Patch(facecolor='orange', alpha=0.7, label='Moderate'),
            Patch(facecolor='red', alpha=0.7, label='Critical')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def create_gap_analysis_chart(self, dates, gaps, classifications):
        """
        Create supply-demand gap analysis visualization.
        
        Args:
            dates: Date range
            gaps: Gap values
            classifications: Gap classifications
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create color mapping
        colors = []
        for classification in classifications:
            if classification == 'Surplus':
                colors.append('green')
            elif classification == 'Adequate':
                colors.append('blue')
            elif classification == 'Moderate Risk':
                colors.append('orange')
            else:  # Critical Risk
                colors.append('red')
        
        # Plot gaps
        bars = ax.bar(dates, gaps, color=colors, alpha=0.7)
        
        # Add horizontal line at zero
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        
        # Formatting
        ax.set_title('Supply-Demand Gap Analysis', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Gap (Supply - Demand)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Date formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, label='Surplus'),
            Patch(facecolor='blue', alpha=0.7, label='Adequate'),
            Patch(facecolor='orange', alpha=0.7, label='Moderate Risk'),
            Patch(facecolor='red', alpha=0.7, label='Critical Risk')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def create_risk_indicator_panel(self, risk_summary):
        """
        Create risk indicator metrics panel.
        
        Args:
            risk_summary: Dictionary containing risk metrics
        """
        st.subheader("📈 Risk Assessment Dashboard")
        
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Overall Risk Level",
                value=risk_summary['overall_risk'],
                delta=f"{risk_summary['critical_percentage']:.1f}% Critical Periods"
            )
        
        with col2:
            st.metric(
                label="Safe Periods",
                value=risk_summary['safe_periods'],
                delta=f"out of {risk_summary['total_periods']} months"
            )
        
        with col3:
            st.metric(
                label="Average Gap",
                value=f"{risk_summary['avg_gap']:+.1f}%",
                delta="Supply vs Demand"
            )
        
        with col4:
            st.metric(
                label="Worst Case Gap",
                value=f"{risk_summary['worst_gap']:+.1f}%",
                delta="Most Critical Period"
            )
        
        # Risk status explanation
        st.markdown("### Risk Status Classification")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("🟢 **Safe**: Storage > 60% capacity")
        with col2:
            st.warning("🟠 **Moderate**: Storage 30-60% capacity")
        with col3:
            st.error("🔴 **Critical**: Storage < 30% capacity")
    
    def create_sample_data(self, forecast_months, population_growth, rainfall_variation, consumption_growth):
        """
        Generate sample data for demonstration.
        In production, this would integrate with the actual modules.
        """
        # Historical data (60 months)
        hist_periods = 60
        dates_hist = pd.date_range(
            end=pd.Timestamp.now().replace(day=1),
            periods=hist_periods,
            freq='MS'
        )
        
        np.random.seed(42)
        
        # Generate historical data with trends
        hist_time = np.arange(hist_periods)
        actual_demand = 700 + 0.5 * hist_time + 50 * np.sin(2 * np.pi * hist_time / 12) + np.random.normal(0, 20, hist_periods)
        actual_demand = np.maximum(actual_demand, 0)
        
        # Generate forecast data
        forecast_dates = pd.date_range(
            start=dates_hist[-1] + pd.DateOffset(months=1),
            periods=forecast_months,
            freq='MS'
        )
        
        # Adjust for scenarios
        base_growth = 1 + consumption_growth
        scenario_factor = (1 + population_growth) * (1 + consumption_growth)
        
        forecast_time = np.arange(forecast_months)
        forecast_demand = actual_demand[-1] * scenario_factor + np.linspace(0, 100 * forecast_months * scenario_factor, forecast_months) + np.random.normal(0, 30, forecast_months)
        forecast_demand = np.maximum(forecast_demand, 0)
        
        # Add confidence intervals
        ci_width = forecast_demand * 0.15  # 15% confidence interval
        lower_ci = forecast_demand - ci_width
        upper_ci = forecast_demand + ci_width
        
        # Reservoir simulation (simplified)
        initial_storage = 1200
        storage_capacity = 2000
        storage_levels = [initial_storage]
        risk_status = []
        
        for i in range(forecast_months):
            inflow = (100 + 80 * np.sin(2 * np.pi * i / 12)) * (1 + rainfall_variation) + np.random.normal(0, 20)
            inflow = max(0, inflow)
            demand = forecast_demand[i]
            loss = storage_levels[-1] * 0.05  # 5% loss
            
            new_storage = storage_levels[-1] + inflow - demand - loss
            new_storage = max(0, min(new_storage, storage_capacity))
            storage_levels.append(new_storage)
            
            # Risk classification
            storage_ratio = new_storage / storage_capacity
            if storage_ratio > 0.6:
                risk_status.append('Safe')
            elif storage_ratio > 0.3:
                risk_status.append('Moderate')
            else:
                risk_status.append('Critical')
        
        storage_levels = storage_levels[1:]  # Remove initial value
        
        # Gap analysis
        gaps = np.array(storage_levels) - np.array(forecast_demand)
        gap_percentages = (gaps / np.array(forecast_demand)) * 100
        
        gap_classifications = []
        for gap_pct in gap_percentages:
            if gap_pct > 20:
                gap_classifications.append('Surplus')
            elif gap_pct > 0:
                gap_classifications.append('Adequate')
            elif gap_pct > -20:
                gap_classifications.append('Moderate Risk')
            else:
                gap_classifications.append('Critical Risk')
        
        # Risk summary
        safe_count = risk_status.count('Safe')
        moderate_count = risk_status.count('Moderate')
        critical_count = risk_status.count('Critical')
        
        risk_summary = {
            'overall_risk': 'Moderate' if critical_count > 2 else 'Low' if critical_count == 0 else 'High',
            'critical_percentage': (critical_count / forecast_months) * 100,
            'safe_periods': safe_count,
            'total_periods': forecast_months,
            'avg_gap': np.mean(gap_percentages),
            'worst_gap': np.min(gap_percentages)
        }
        
        return {
            'dates_hist': dates_hist,
            'actual_demand': actual_demand,
            'forecast_dates': forecast_dates,
            'forecast_demand': forecast_demand,
            'lower_ci': lower_ci,
            'upper_ci': upper_ci,
            'storage_dates': forecast_dates,
            'storage_levels': storage_levels,
            'risk_status': risk_status,
            'gap_dates': forecast_dates,
            'gaps': gaps,
            'gap_classifications': gap_classifications,
            'risk_summary': risk_summary
        }
    
    def run_dashboard(self):
        """Main dashboard execution function."""
        # Setup
        self.create_header()
        sidebar_params = self.setup_sidebar()
        
        # Main content area
        if sidebar_params['run_simulation']:
            with st.spinner("Running water resource simulation..."):
                # Generate sample data (in production, integrate with actual modules)
                data = self.create_sample_data(
                    sidebar_params['forecast_months'],
                    sidebar_params['population_growth'],
                    sidebar_params['rainfall_variation'],
                    sidebar_params['consumption_growth']
                )
                
                # Create tabs for different visualizations
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Demand Forecast", 
                    "💧 Reservoir Storage", 
                    "⚖️ Gap Analysis", 
                    "📈 Risk Dashboard"
                ])
                
                with tab1:
                    st.subheader("Water Demand Forecasting")
                    fig1 = self.create_demand_forecast_chart(
                        list(data['dates_hist']) + list(data['forecast_dates']),
                        data['actual_demand'],
                        data['forecast_demand'],
                        data['lower_ci'],
                        data['upper_ci']
                    )
                    st.pyplot(fig1)
                    
                    # Forecast metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Forecast Period", f"{sidebar_params['forecast_months']} months")
                    with col2:
                        st.metric("Average Forecast Demand", f"{np.mean(data['forecast_demand']):.0f} units")
                    with col3:
                        st.metric("Forecast Growth Rate", f"{((data['forecast_demand'][-1]/data['forecast_demand'][0])**(12/sidebar_params['forecast_months'])-1)*100:+.1f}% annual")
                
                with tab2:
                    st.subheader("Reservoir Storage Simulation")
                    fig2 = self.create_reservoir_storage_chart(
                        data['storage_dates'],
                        data['storage_levels'],
                        data['risk_status']
                    )
                    st.pyplot(fig2)
                    
                    # Storage metrics
                    st.markdown("### Storage Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Initial Storage", f"{data['storage_levels'][0]:.0f} units")
                    with col2:
                        st.metric("Final Storage", f"{data['storage_levels'][-1]:.0f} units")
                    with col3:
                        st.metric("Min Storage", f"{min(data['storage_levels']):.0f} units")
                    with col4:
                        st.metric("Max Storage", f"{max(data['storage_levels']):.0f} units")
                
                with tab3:
                    st.subheader("Supply-Demand Gap Analysis")
                    fig3 = self.create_gap_analysis_chart(
                        data['gap_dates'],
                        data['gaps'],
                        data['gap_classifications']
                    )
                    st.pyplot(fig3)
                    
                    # Gap statistics
                    gap_df = pd.DataFrame({
                        'Classification': data['gap_classifications'],
                        'Count': [data['gap_classifications'].count(c) for c in set(data['gap_classifications'])]
                    })
                    st.dataframe(gap_df)
                
                with tab4:
                    self.create_risk_indicator_panel(data['risk_summary'])
                    
                    # Detailed risk breakdown
                    st.markdown("### Risk Period Breakdown")
                    risk_counts = pd.Series(data['risk_status']).value_counts()
                    st.bar_chart(risk_counts)
                    
                    # Scenario parameters summary
                    st.markdown("### Scenario Parameters")
                    param_df = pd.DataFrame({
                        'Parameter': ['Population Growth', 'Rainfall Variation', 'Consumption Growth'],
                        'Value': [f"{sidebar_params['population_growth']*100:+.1f}%", 
                                 f"{sidebar_params['rainfall_variation']*100:+.1f}%", 
                                 f"{sidebar_params['consumption_growth']*100:+.1f}%"]
                    })
                    st.table(param_df)
        else:
            # Show welcome message
            st.info("👈 Adjust parameters in the sidebar and click 'Run Simulation' to start the analysis")
            
            # Show system overview
            st.markdown("### System Capabilities")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📊 Forecasting**")
                st.markdown("- ARIMA time series modeling\n- Demand forecasting\n- Confidence intervals")
            
            with col2:
                st.markdown("**💧 Simulation**")
                st.markdown("- Reservoir storage modeling\n- Water balance equations\n- Risk assessment")
            
            with col3:
                st.markdown("**⚖️ Analysis**")
                st.markdown("- Supply-demand gap analysis\n- Scenario modeling\n- Risk classification")

def main():
    """Main function to run the dashboard."""
    dashboard = AquaPredictDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()