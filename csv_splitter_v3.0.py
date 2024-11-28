import os
import pandas as pd
from datetime import datetime, timedelta

def sanitize_filename(filename):
    """Sanitize filenames to ensure compatibility with all operating systems."""
    return ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in filename)

def week_number_from_date(date):
    """Get the week number and year from a date."""
    return date.isocalendar().week, date.year

def split_csv_by_week(input_file, output_base_dir):
    """
    Split the CSV data into weekly chunks based on the timestamp column.
    Data cleaning (removing NULL values) is applied before splitting.
    """
    # Load data and parse Timestamp column
    try:
        df = pd.read_csv(input_file, parse_dates=['Timestamp'], na_values=['NULL'])
    except Exception as e:
        print(f"Error reading the file: {e}")
        return
    
    # Remove rows with missing Timestamps
    if 'Timestamp' not in df.columns:
        print("Error: The required 'Timestamp' column is missing in the dataset.")
        return

    df = df.dropna(subset=['Timestamp'])

    # Ensure Timestamp is sorted
    df = df.sort_values('Timestamp')

    # Create a week number column
    df['Week'] = df['Timestamp'].dt.isocalendar().week
    df['Year'] = df['Timestamp'].dt.year

    # Group by week and year
    grouped = df.groupby(['Year', 'Week'])

    for (year, week), group in grouped:
        # Create folder structure based on location (Office in this case)
        location = "Office"  # Fixed as Office for now
        folder_name = os.path.join(output_base_dir, f"{year}_W{week:02d}_{location}")
        os.makedirs(folder_name, exist_ok=True)

        # Save the weekly data to a CSV file
        filename = f"PUA_W{week:02d}_{location}_{year}.csv"
        output_path = os.path.join(folder_name, sanitize_filename(filename))
        group.drop(columns=['Week', 'Year']).to_csv(output_path, index=False)
        print(f"Saved file: {output_path}")

def main():
    """
    Main program to interact with the user and split the CSV by weekly data.
    """
    output_base_dir = r"D:\PUA_analysis"  # Output directory

    while True:
        input_file = input("Enter the full path of the CSV file to split (or 'q' to quit): ").strip()
        if input_file.lower() == 'q':
            break
        
        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist. Please try again.")
            continue
        
        try:
            # Split the file by week
            split_csv_by_week(input_file, output_base_dir)
        except Exception as e:
            print(f"An error occurred: {e}")
        
        another = input("Do you want to process another file? (y/n): ").strip().lower()
        if another != 'y':
            break

    print("Processing complete. Goodbye!")

if __name__ == "__main__":
    main()