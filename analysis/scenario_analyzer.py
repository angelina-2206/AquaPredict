"""
Scenario analysis module for AquaPredict system.
Supports analysis of different water demand and supply scenarios.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class ScenarioAnalyzer:
    """
    A class to analyze different water resource scenarios.
    """
    
    def __init__(self):
        """Initialize the scenario analyzer."""
        self.scenarios = {}
        self.baseline_results = None
    
    def adjust_for_population_growth(self, base_data, growth_rate, periods):
        """
        Adjust data for population growth.
        
        Args:
            base_data (list or array): Base data values
            growth_rate (float): Annual growth rate (as decimal, e.g., 0.03 for 3%)
            periods (int): Number of periods to project
            
        Returns:
            list: Adjusted data with population growth
        """
        adjusted_data = []
        current_value = base_data[-1] if isinstance(base_data, list) else base_data
        
        for i in range(periods):
            # Apply compound growth
            growth_factor = (1 + growth_rate) ** (i + 1)
            adjusted_value = current_value * growth_factor
            adjusted_data.append(adjusted_value)
        
        return adjusted_data
    
    def adjust_for_rainfall_variation(self, base_rainfall, variation_percentage):
        """
        Adjust rainfall data for variation scenarios.
        
        Args:
            base_rainfall (list or array): Base rainfall data
            variation_percentage (float): Variation percentage (e.g., -0.2 for 20% decrease)
            
        Returns:
            list: Adjusted rainfall data
        """
        if isinstance(base_rainfall, list):
            adjusted_rainfall = [r * (1 + variation_percentage) for r in base_rainfall]
        else:
            adjusted_rainfall = base_rainfall * (1 + variation_percentage)
        
        return adjusted_rainfall
    
    def adjust_for_consumption_growth(self, base_consumption, growth_rate, periods):
        """
        Adjust consumption data for growth trends.
        
        Args:
            base_consumption (list or array): Base consumption data
            growth_rate (float): Growth rate per period
            periods (int): Number of periods to project
            
        Returns:
            list: Adjusted consumption data
        """
        return self.adjust_for_population_growth(base_consumption, growth_rate, periods)
    
    def create_baseline_scenario(self, demand_forecast, reservoir_data, periods):
        """
        Create baseline scenario with current conditions.
        
        Args:
            demand_forecast (list or array): Forecasted demand
            reservoir_data (list or array): Reservoir storage data
            periods (int): Number of periods
            
        Returns:
            dict: Baseline scenario results
        """
        # For baseline, use provided data directly
        baseline_results = {
            'name': 'Baseline Scenario',
            'description': 'Current conditions and trends',
            'demand': demand_forecast[:periods] if len(demand_forecast) >= periods else demand_forecast,
            'supply': reservoir_data[:periods] if len(reservoir_data) >= periods else reservoir_data,
            'parameters': {
                'population_growth': 0,
                'rainfall_variation': 0,
                'consumption_growth': 0
            }
        }
        
        self.baseline_results = baseline_results
        return baseline_results
    
    def create_drought_scenario(self, baseline_demand, baseline_supply, 
                              demand_growth_rate=0.02, rainfall_decrease=-0.3, periods=12):
        """
        Create drought scenario with reduced rainfall and increased demand.
        
        Args:
            baseline_demand (list): Baseline demand data
            baseline_supply (list): Baseline supply data
            demand_growth_rate (float): Additional demand growth rate
            rainfall_decrease (float): Rainfall reduction percentage
            periods (int): Number of periods to simulate
            
        Returns:
            dict: Drought scenario results
        """
        # Adjust demand for growth
        adjusted_demand = self.adjust_for_consumption_growth(
            baseline_demand, demand_growth_rate, periods
        )
        
        # Adjust supply for reduced rainfall
        adjusted_supply = self.adjust_for_rainfall_variation(
            baseline_supply, rainfall_decrease
        )
        
        # Ensure we have enough periods
        if len(adjusted_supply) < periods:
            # Extend the supply data if needed
            last_value = adjusted_supply[-1] if len(adjusted_supply) > 0 else baseline_supply[-1]
            extension = [last_value * (1 + rainfall_decrease)] * (periods - len(adjusted_supply))
            adjusted_supply = list(adjusted_supply) + extension
        else:
            adjusted_supply = adjusted_supply[:periods]
        
        drought_results = {
            'name': 'Drought Scenario',
            'description': '30% reduction in rainfall with 2% annual demand growth',
            'demand': adjusted_demand,
            'supply': adjusted_supply,
            'parameters': {
                'population_growth': demand_growth_rate,
                'rainfall_variation': rainfall_decrease,
                'consumption_growth': demand_growth_rate
            }
        }
        
        return drought_results
    
    def create_high_growth_scenario(self, baseline_demand, baseline_supply,
                                  population_growth_rate=0.05, 
                                  consumption_growth_rate=0.04, 
                                  rainfall_variation=0.1, periods=12):
        """
        Create high growth scenario with increased population and consumption.
        
        Args:
            baseline_demand (list): Baseline demand data
            baseline_supply (list): Baseline supply data
            population_growth_rate (float): Population growth rate
            consumption_growth_rate (float): Consumption growth rate
            rainfall_variation (float): Rainfall variation percentage
            periods (int): Number of periods to simulate
            
        Returns:
            dict: High growth scenario results
        """
        # Adjust for high growth
        adjusted_demand = self.adjust_for_consumption_growth(
            baseline_demand, consumption_growth_rate, periods
        )
        
        # Adjust supply for rainfall variation
        adjusted_supply = self.adjust_for_rainfall_variation(
            baseline_supply, rainfall_variation
        )
        
        # Ensure we have enough periods
        if len(adjusted_supply) < periods:
            last_value = adjusted_supply[-1] if len(adjusted_supply) > 0 else baseline_supply[-1]
            extension = [last_value * (1 + rainfall_variation)] * (periods - len(adjusted_supply))
            adjusted_supply = list(adjusted_supply) + extension
        else:
            adjusted_supply = adjusted_supply[:periods]
        
        high_growth_results = {
            'name': 'High Growth Scenario',
            'description': '5% population growth, 4% consumption growth, 10% rainfall increase',
            'demand': adjusted_demand,
            'supply': adjusted_supply,
            'parameters': {
                'population_growth': population_growth_rate,
                'rainfall_variation': rainfall_variation,
                'consumption_growth': consumption_growth_rate
            }
        }
        
        return high_growth_results
    
    def create_custom_scenario(self, name, description, baseline_demand, baseline_supply,
                             population_growth=0, rainfall_variation=0, 
                             consumption_growth=0, periods=12):
        """
        Create a custom scenario with specified parameters.
        
        Args:
            name (str): Scenario name
            description (str): Scenario description
            baseline_demand (list): Baseline demand data
            baseline_supply (list): Baseline supply data
            population_growth (float): Population growth rate
            rainfall_variation (float): Rainfall variation percentage
            consumption_growth (float): Consumption growth rate
            periods (int): Number of periods
            
        Returns:
            dict: Custom scenario results
        """
        # Adjust demand
        adjusted_demand = self.adjust_for_consumption_growth(
            baseline_demand, consumption_growth, periods
        )
        
        # Adjust supply
        adjusted_supply = self.adjust_for_rainfall_variation(
            baseline_supply, rainfall_variation
        )
        
        # Ensure we have enough periods
        if len(adjusted_supply) < periods:
            last_value = adjusted_supply[-1] if len(adjusted_supply) > 0 else baseline_supply[-1]
            extension = [last_value * (1 + rainfall_variation)] * (periods - len(adjusted_supply))
            adjusted_supply = list(adjusted_supply) + extension
        else:
            adjusted_supply = adjusted_supply[:periods]
        
        custom_results = {
            'name': name,
            'description': description,
            'demand': adjusted_demand,
            'supply': adjusted_supply,
            'parameters': {
                'population_growth': population_growth,
                'rainfall_variation': rainfall_variation,
                'consumption_growth': consumption_growth
            }
        }
        
        return custom_results
    
    def compare_scenarios(self, scenarios_list):
        """
        Compare multiple scenarios side by side.
        
        Args:
            scenarios_list (list): List of scenario dictionaries
            
        Returns:
            pd.DataFrame: Comparison summary
        """
        comparison_data = []
        
        for scenario in scenarios_list:
            # Calculate summary statistics
            demand_avg = np.mean(scenario['demand'])
            supply_avg = np.mean(scenario['supply'])
            avg_gap = supply_avg - demand_avg
            gap_percentage = (avg_gap / demand_avg) * 100 if demand_avg > 0 else 0
            
            # Count risk periods
            gaps = np.array(scenario['supply']) - np.array(scenario['demand'])
            gap_percentages = (gaps / np.array(scenario['demand'])) * 100
            critical_periods = np.sum(gap_percentages < -20)
            moderate_periods = np.sum((gap_percentages >= -20) & (gap_percentages < 0))
            surplus_periods = np.sum(gap_percentages > 0)
            
            comparison_data.append({
                'Scenario': scenario['name'],
                'Description': scenario['description'],
                'Avg_Demand': round(demand_avg, 2),
                'Avg_Supply': round(supply_avg, 2),
                'Avg_Gap': round(avg_gap, 2),
                'Gap_%': round(gap_percentage, 2),
                'Critical_Periods': critical_periods,
                'Moderate_Periods': moderate_periods,
                'Surplus_Periods': surplus_periods,
                'Population_Growth': f"{scenario['parameters']['population_growth']*100:.1f}%",
                'Rainfall_Variation': f"{scenario['parameters']['rainfall_variation']*100:+.1f}%",
                'Consumption_Growth': f"{scenario['parameters']['consumption_growth']*100:.1f}%"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        return comparison_df
    
    def generate_scenario_report(self, scenarios_list):
        """
        Generate comprehensive scenario analysis report.
        
        Args:
            scenarios_list (list): List of scenario dictionaries
            
        Returns:
            dict: Detailed scenario report
        """
        comparison_df = self.compare_scenarios(scenarios_list)
        
        # Find best and worst scenarios
        best_scenario = comparison_df.loc[comparison_df['Gap_%'].idxmax()]
        worst_scenario = comparison_df.loc[comparison_df['Gap_%'].idxmin()]
        
        # Risk assessment
        risk_levels = []
        for _, row in comparison_df.iterrows():
            if row['Gap_%'] > 10:
                risk_levels.append('Low Risk')
            elif row['Gap_%'] > 0:
                risk_levels.append('Moderate Risk')
            elif row['Gap_%'] > -20:
                risk_levels.append('High Risk')
            else:
                risk_levels.append('Very High Risk')
        
        comparison_df['Risk_Level'] = risk_levels
        
        report = {
            'comparison_table': comparison_df,
            'best_scenario': {
                'name': best_scenario['Scenario'],
                'gap_percentage': best_scenario['Gap_%']
            },
            'worst_scenario': {
                'name': worst_scenario['Scenario'],
                'gap_percentage': worst_scenario['Gap_%']
            },
            'recommendations': self._generate_recommendations(comparison_df)
        }
        
        return report
    
    def _generate_recommendations(self, comparison_df):
        """
        Generate recommendations based on scenario analysis.
        
        Args:
            comparison_df (pd.DataFrame): Comparison results
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        # Check for high-risk scenarios
        high_risk_scenarios = comparison_df[comparison_df['Gap_%'] < -10]
        if len(high_risk_scenarios) > 0:
            recommendations.append(
                "⚠️ High risk scenarios detected. Consider water conservation measures and demand management."
            )
        
        # Check for scenarios with many critical periods
        critical_scenarios = comparison_df[comparison_df['Critical_Periods'] > 3]
        if len(critical_scenarios) > 0:
            recommendations.append(
                "🚨 Multiple critical periods identified. Emergency water allocation planning recommended."
            )
        
        # Check for positive scenarios
        positive_scenarios = comparison_df[comparison_df['Gap_%'] > 10]
        if len(positive_scenarios) > 0:
            recommendations.append(
                "✅ Favorable conditions in some scenarios. Opportunity for strategic water storage."
            )
        
        if len(recommendations) == 0:
            recommendations.append(
                "📊 All scenarios show moderate conditions. Continue monitoring and adaptive management."
            )
        
        return recommendations

def main():
    """Main function to demonstrate scenario analysis."""
    # Sample baseline data
    np.random.seed(42)
    
    periods = 12
    baseline_demand = [800 + i*10 + np.random.normal(0, 20) for i in range(periods)]
    baseline_supply = [1000 + 100*np.sin(2*np.pi*i/12) + np.random.normal(0, 50) for i in range(periods)]
    
    # Initialize analyzer
    analyzer = ScenarioAnalyzer()
    
    # Create scenarios
    print("Creating scenarios...")
    
    baseline = analyzer.create_baseline_scenario(baseline_demand, baseline_supply, periods)
    drought = analyzer.create_drought_scenario(baseline_demand, baseline_supply)
    high_growth = analyzer.create_high_growth_scenario(baseline_demand, baseline_supply)
    
    # Create custom scenario
    custom = analyzer.create_custom_scenario(
        name="Conservation Scenario",
        description="2% population growth, 30% rainfall increase, 1% consumption reduction",
        baseline_demand=baseline_demand,
        baseline_supply=baseline_supply,
        population_growth=0.02,
        rainfall_variation=0.3,
        consumption_growth=-0.01,
        periods=periods
    )
    
    # Compare scenarios
    scenarios = [baseline, drought, high_growth, custom]
    comparison = analyzer.compare_scenarios(scenarios)
    
    print("\nScenario Comparison:")
    print(comparison[['Scenario', 'Avg_Demand', 'Avg_Supply', 'Gap_%', 'Critical_Periods']])
    
    # Generate detailed report
    print("\n" + "="*60)
    print("SCENARIO ANALYSIS REPORT")
    print("="*60)
    
    report = analyzer.generate_scenario_report(scenarios)
    
    print(f"Best Scenario: {report['best_scenario']['name']} (Gap: {report['best_scenario']['gap_percentage']}%)")
    print(f"Worst Scenario: {report['worst_scenario']['name']} (Gap: {report['worst_scenario']['gap_percentage']}%)")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"• {rec}")

if __name__ == "__main__":
    main()