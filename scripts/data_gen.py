#!/usr/bin/env python3
"""
Data Generation Script for COVID-19 Dashboard
Generates sample COVID-19 cases and deaths data with realistic patterns
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

def generate_covid_data():
    """Generate realistic COVID-19 cases and deaths data"""
    
    # Create date range for 18 weeks
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(18)]
    week_labels = [date.strftime('%b %d') for date in dates]
    
    # Generate realistic case numbers with some seasonality and decline
    np.random.seed(42)  # For reproducibility
    
    # Base case numbers with declining trend
    base_cases = np.linspace(45000, 19000, 18)
    # Add some randomness and seasonal variation
    noise = np.random.normal(0, 3000, 18)
    seasonal_factor = 1 + 0.3 * np.sin(np.linspace(0, 2*np.pi, 18))
    
    cases = base_cases * seasonal_factor + noise
    cases = np.maximum(cases, 15000)  # Ensure minimum case count
    cases = cases.astype(int)
    
    # Generate deaths with 2-3 week lag and lower numbers
    # Deaths follow cases with some delay and case fatality rate ~2-6%
    death_base = np.roll(cases, 2) * 0.025  # 2.5% base fatality rate
    death_noise = np.random.normal(0, 50, 18)
    deaths = death_base + death_noise
    deaths = np.maximum(deaths, 200)  # Ensure minimum death count
    deaths = deaths.astype(int)
    
    return dates, week_labels, cases, deaths

def create_summary_stats(cases, deaths):
    """Create summary statistics for the dashboard"""
    total_cases_28d = sum(cases[-4:])  # Last 4 weeks
    total_deaths_28d = sum(deaths[-4:])  # Last 4 weeks
    case_fatality_rate = (total_deaths_28d / total_cases_28d) * 100
    reporting_countries = 89  # Static number from WHO data
    
    return {
        'total_cases_28d': total_cases_28d,
        'total_deaths_28d': total_deaths_28d,
        'case_fatality_rate': case_fatality_rate,
        'reporting_countries': reporting_countries
    }

def main():
    """Main function to generate and save data"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate data
    dates, week_labels, cases, deaths = generate_covid_data()
    stats = create_summary_stats(cases, deaths)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'week_label': week_labels,
        'cases': cases,
        'deaths': deaths
    })
    
    # Save as CSV
    df.to_csv('data/dataframe.csv', index=False)
    print(f"✓ Saved main data to data/dataframe.csv")
    
    # Create a secondary dataframe with summary stats
    stats_df = pd.DataFrame([stats])
    stats_df.to_csv('data/dataframe2.csv', index=False)
    print(f"✓ Saved summary stats to data/dataframe2.csv")
    
    # Save raw numpy arrays
    data_array = np.column_stack([cases, deaths])
    np.save('data/sample.npy', data_array)
    print(f"✓ Saved numpy array to data/sample.npy")
    
    # Print summary
    print("\n" + "="*50)
    print("DATA GENERATION SUMMARY")
    print("="*50)
    print(f"Total weeks generated: {len(week_labels)}")
    print(f"Date range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
    print(f"Cases range: {cases.min():,} to {cases.max():,}")
    print(f"Deaths range: {deaths.min():,} to {deaths.max():,}")
    print(f"28-day totals: {stats['total_cases_28d']:,} cases, {stats['total_deaths_28d']:,} deaths")
    print(f"Case fatality rate: {stats['case_fatality_rate']:.1f}%")
    print("\nFirst few rows of generated data:")
    print(df.head())

if __name__ == "__main__":
    main()