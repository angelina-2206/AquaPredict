"""
Supply-demand gap analysis module for AquaPredict system.
Analyzes the difference between water supply and demand.
"""

import pandas as pd
import numpy as np

class GapAnalyzer:
    """
    A class to analyze supply-demand gaps in water resources.
    """
    
    def __init__(self):
        """Initialize the gap analyzer."""
        self.gap_results = None
        self.risk_classification = None
    
    def calculate_gap(self, supply_data, demand_data, dates=None):
        """
        Calculate supply-demand gap for each period.
        
        Args:
            supply_data (list or array): Supply values
            demand_data (list or array): Demand values
            dates (list): Date labels for each period
            
        Returns:
            pd.DataFrame: Gap analysis results
        """
        # Ensure data arrays are same length
        min_length = min(len(supply_data), len(demand_data))
        supply_data = supply_data[:min_length]
        demand_data = demand_data[:min_length]
        
        if dates is not None:
            dates = dates[:min_length]
        else:
            dates = pd.date_range(
                start=pd.Timestamp.now().replace(day=1),
                periods=min_length,
                freq='MS'
            )
        
        # Calculate gaps
        gaps = np.array(supply_data) - np.array(demand_data)
        gap_percentages = (gaps / np.array(demand_data)) * 100
        
        # Classify gaps
        gap_classification = []
        for gap, gap_pct in zip(gaps, gap_percentages):
            if gap > 0:
                if gap_pct > 20:  # Surplus > 20%
                    gap_classification.append('Surplus')
                else:  # 0-20% surplus
                    gap_classification.append('Adequate')
            else:
                if gap_pct < -20:  # Deficit > 20%
                    gap_classification.append('Critical Risk')
                else:  # 0-20% deficit
                    gap_classification.append('Moderate Risk')
        
        # Create results dataframe
        results_df = pd.DataFrame({
            'date': dates,
            'supply': supply_data,
            'demand': demand_data,
            'gap': gaps,
            'gap_percentage': gap_percentages,
            'classification': gap_classification
        })
        
        self.gap_results = results_df
        return results_df
    
    def classify_risk_periods(self, critical_threshold=-20, moderate_threshold=-5):
        """
        Classify periods based on risk levels.
        
        Args:
            critical_threshold (float): Percentage threshold for critical risk
            moderate_threshold (float): Percentage threshold for moderate risk
            
        Returns:
            dict: Risk period classification
        """
        if self.gap_results is None:
            raise ValueError("No gap analysis results available. Run calculate_gap() first.")
        
        df = self.gap_results
        
        risk_periods = {
            'surplus': df[df['classification'] == 'Surplus'],
            'adequate': df[df['classification'] == 'Adequate'],
            'moderate_risk': df[df['classification'] == 'Moderate Risk'],
            'critical_risk': df[df['classification'] == 'Critical Risk']
        }
        
        self.risk_classification = risk_periods
        return risk_periods
    
    def get_summary_report(self):
        """
        Generate summary report of gap analysis.
        
        Returns:
            dict: Summary statistics and key findings
        """
        if self.gap_results is None:
            raise ValueError("No gap analysis results available")
        
        df = self.gap_results
        
        # Calculate summary statistics
        total_periods = len(df)
        surplus_periods = len(df[df['classification'] == 'Surplus'])
        adequate_periods = len(df[df['classification'] == 'Adequate'])
        moderate_risk_periods = len(df[df['classification'] == 'Moderate Risk'])
        critical_risk_periods = len(df[df['classification'] == 'Critical Risk'])
        
        # Calculate average metrics
        avg_supply = df['supply'].mean()
        avg_demand = df['demand'].mean()
        avg_gap = df['gap'].mean()
        avg_gap_percentage = df['gap_percentage'].mean()
        
        # Find worst and best periods
        worst_period = df.loc[df['gap_percentage'].idxmin()]
        best_period = df.loc[df['gap_percentage'].idxmax()]
        
        summary = {
            'total_periods_analyzed': total_periods,
            'period_distribution': {
                'surplus_periods': surplus_periods,
                'adequate_periods': adequate_periods,
                'moderate_risk_periods': moderate_risk_periods,
                'critical_risk_periods': critical_risk_periods
            },
            'average_metrics': {
                'average_supply': round(avg_supply, 2),
                'average_demand': round(avg_demand, 2),
                'average_gap': round(avg_gap, 2),
                'average_gap_percentage': round(avg_gap_percentage, 2)
            },
            'critical_periods': {
                'count': critical_risk_periods,
                'percentage': round((critical_risk_periods / total_periods) * 100, 2)
            },
            'risk_level': self._determine_overall_risk(critical_risk_periods, total_periods),
            'worst_period': {
                'date': worst_period['date'],
                'supply': round(worst_period['supply'], 2),
                'demand': round(worst_period['demand'], 2),
                'gap_percentage': round(worst_period['gap_percentage'], 2),
                'classification': worst_period['classification']
            },
            'best_period': {
                'date': best_period['date'],
                'supply': round(best_period['supply'], 2),
                'demand': round(best_period['demand'], 2),
                'gap_percentage': round(best_period['gap_percentage'], 2),
                'classification': best_period['classification']
            }
        }
        
        return summary
    
    def _determine_overall_risk(self, critical_periods, total_periods):
        """
        Determine overall risk level for the analysis period.
        
        Args:
            critical_periods (int): Number of critical risk periods
            total_periods (int): Total number of periods
            
        Returns:
            str: Overall risk assessment
        """
        critical_percentage = (critical_periods / total_periods) * 100
        
        if critical_percentage == 0:
            return 'Low Risk'
        elif critical_percentage <= 20:
            return 'Moderate Risk'
        elif critical_percentage <= 50:
            return 'High Risk'
        else:
            return 'Very High Risk'
    
    def get_monthly_trends(self):
        """
        Analyze monthly trends in supply-demand gaps.
        
        Returns:
            pd.DataFrame: Monthly trend analysis
        """
        if self.gap_results is None:
            raise ValueError("No gap analysis results available")
        
        df = self.gap_results.copy()
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['year'] = pd.to_datetime(df['date']).dt.year
        
        # Group by month and calculate averages
        monthly_trends = df.groupby('month').agg({
            'supply': 'mean',
            'demand': 'mean',
            'gap': 'mean',
            'gap_percentage': 'mean'
        }).round(2)
        
        # Add month names
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_trends['month_name'] = [month_names[i-1] for i in monthly_trends.index]
        
        return monthly_trends
    
    def identify_vulnerable_months(self, threshold=-10):
        """
        Identify months that are consistently vulnerable.
        
        Args:
            threshold (float): Gap percentage threshold for vulnerability
            
        Returns:
            pd.DataFrame: Vulnerable months analysis
        """
        if self.gap_results is None:
            raise ValueError("No gap analysis results available")
        
        df = self.gap_results.copy()
        df['month'] = pd.to_datetime(df['date']).dt.month
        
        # Calculate average gap percentage by month
        monthly_avg = df.groupby('month')['gap_percentage'].mean()
        
        # Identify vulnerable months
        vulnerable_months = monthly_avg[monthly_avg < threshold]
        
        if len(vulnerable_months) > 0:
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            vulnerable_analysis = pd.DataFrame({
                'month': vulnerable_months.index,
                'month_name': [month_names[i-1] for i in vulnerable_months.index],
                'avg_gap_percentage': vulnerable_months.values
            }).sort_values('avg_gap_percentage')
            
            return vulnerable_analysis
        else:
            return pd.DataFrame(columns=['month', 'month_name', 'avg_gap_percentage'])

def main():
    """Main function to demonstrate gap analysis."""
    # Sample data for demonstration
    np.random.seed(42)
    
    # Create sample data (12 months)
    periods = 12
    dates = pd.date_range(start='2024-01-01', periods=periods, freq='MS')
    
    # Sample supply data (reservoir storage)
    base_supply = 1000
    supply_data = base_supply + 200 * np.sin(2 * np.pi * np.arange(periods) / 12) + np.random.normal(0, 100, periods)
    supply_data = np.maximum(supply_data, 0)
    
    # Sample demand data
    base_demand = 800
    demand_data = base_demand + np.linspace(0, 150, periods) + np.random.normal(0, 50, periods)
    demand_data = np.maximum(demand_data, 0)
    
    # Initialize analyzer
    analyzer = GapAnalyzer()
    
    # Calculate gaps
    print("Calculating supply-demand gaps...")
    gap_results = analyzer.calculate_gap(supply_data, demand_data, dates)
    
    # Display results
    print("\nGap Analysis Results:")
    print(gap_results[['date', 'supply', 'demand', 'gap', 'gap_percentage', 'classification']])
    
    # Classify risk periods
    risk_periods = analyzer.classify_risk_periods()
    
    print(f"\nRisk Period Classification:")
    for risk_level, periods_df in risk_periods.items():
        print(f"{risk_level.replace('_', ' ').title()}: {len(periods_df)} periods")
    
    # Summary report
    print("\n" + "="*50)
    print("SUMMARY REPORT")
    print("="*50)
    summary = analyzer.get_summary_report()
    
    print(f"Total Periods Analyzed: {summary['total_periods_analyzed']}")
    print(f"Overall Risk Level: {summary['risk_level']}")
    print(f"Critical Risk Periods: {summary['critical_periods']['count']} ({summary['critical_periods']['percentage']}%)")
    
    print(f"\nAverage Supply: {summary['average_metrics']['average_supply']}")
    print(f"Average Demand: {summary['average_metrics']['average_demand']}")
    print(f"Average Gap: {summary['average_metrics']['average_gap']}")
    
    print(f"\nWorst Period: {summary['worst_period']['date'].strftime('%Y-%m')}")
    print(f"  Gap: {summary['worst_period']['gap_percentage']}% ({summary['worst_period']['classification']})")
    
    print(f"\nBest Period: {summary['best_period']['date'].strftime('%Y-%m')}")
    print(f"  Gap: {summary['best_period']['gap_percentage']}% ({summary['best_period']['classification']})")
    
    # Monthly trends
    print("\nMonthly Trends:")
    monthly_trends = analyzer.get_monthly_trends()
    print(monthly_trends[['month_name', 'supply', 'demand', 'gap_percentage']])

if __name__ == "__main__":
    main()