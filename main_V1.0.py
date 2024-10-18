import os
import pandas as pd
import numpy as np
from data_processing import load_data, preprocess_data, verify_file_format
from statistical_analysis import generate_statistical_summary, calculate_correlations, calculate_daily_stats
from visualization import plot_time_series, create_combined_pressure_plot, create_correlation_heatmap
from outlier_detection import detect_outliers_isolation_forest, summarize_outliers
from report_generation import generate_pdf_report

def analyze_data(input_file, output_dir):
    df = load_data(input_file)
    df = preprocess_data(df)
    
    output_file = os.path.join(output_dir, f"analysis_report_{df.index[0].strftime('%Y-%m-%d')}.pdf")
    
    stats = generate_statistical_summary(df)
    correlations = calculate_correlations(df)
    outliers = detect_outliers_isolation_forest(df)
    
    time_series_figures = plot_time_series(df, df.select_dtypes(include=[np.number]).columns)
    combined_pressure_fig = create_combined_pressure_plot(df)
    correlation_heatmap_fig = create_correlation_heatmap(df)
    
    all_figures = time_series_figures + [("Combined Pressure and Pump Values", combined_pressure_fig)]
    if correlation_heatmap_fig is not None:
        all_figures.append(("Correlation Heatmap", correlation_heatmap_fig))
    
    generate_pdf_report(output_file, df, stats, all_figures, outliers, correlations)
    print(f"Analysis complete. Report saved as: {output_file}")    
    
def main():
    output_dir = r"D:\Csv analytics\csv_data_to_analyze\output"
    os.makedirs(output_dir, exist_ok=True)
    
    while True:
        input_file = input("Please enter the full path of the CSV file you want to analyze (or 'q' to quit): ").strip()
        
        if input_file.lower() == 'q':
            break
        
        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist. Please try again.")
            continue
        
        if not verify_file_format(input_file):
            print("Error: File format is incorrect. Please use a file with the format: output_by_day_YYYY-MM-DD-to-YYYY-MM-DD.csv")
            continue
        
        df = load_data(input_file)
        
        print("\nPlease choose an analysis option:")
        print("1. Analyze the entire file as one unit")
        print("2. Split the analysis into separate reports for each day (7AM to 7AM)")
        print("3. Specify a custom date range for analysis")
        
        choice = input("Enter your choice (1, 2, or 3): ").strip()
        
        if choice == '1':
            analyze_data(input_file, output_dir)
        elif choice == '2':
            # Split the dataframe into days and analyze each day
            start_time = df.index[0].replace(hour=7, minute=0, second=0, microsecond=0)
            end_time = df.index[-1]
            current_day = start_time
            
            while current_day < end_time:
                next_day = current_day + pd.Timedelta(days=1)
                day_df = df[(df.index >= current_day) & (df.index < next_day)]
                
                if not day_df.empty:
                    day_output_file = os.path.join(output_dir, f"analysis_report_{current_day.strftime('%Y-%m-%d')}.pdf")
                    analyze_data(day_df, output_dir)
                    print(f"Analysis complete for {current_day.strftime('%Y-%m-%d')}. Report saved in the output directory.")
                
                current_day = next_day
            
        elif choice == '3':
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            
            try:
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                custom_df = df[(df.index >= start_date) & (df.index <= end_date)]
                
                if not custom_df.empty:
                    analyze_data(custom_df, output_dir)
                else:
                    print("No data found in the specified date range.")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()