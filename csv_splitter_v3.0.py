import os
import pandas as pd
from datetime import datetime, timedelta

def sanitize_filename(filename):
    """Sanitize filenames to ensure compatibility with all operating systems."""
    return ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in filename)

def calculate_shifted_date(timestamp):
    """
    Adjust timestamp for a 7AM-7AM operational day.
    If the timestamp is before 7AM, associate it with the previous day.
    """
    if pd.isnull(timestamp):
        return None  # Return None for invalid timestamps
    if timestamp.hour < 7:
        return (timestamp - timedelta(days=1)).date()
    return timestamp.date()

def split_csv_by_day(input_file, output_base_dir):
    """
    Split the CSV data into daily chunks based on the timestamp column
    with a 7AM-7AM operational day adjustment.
    """
    try:
        # Load and parse the CSV (no data cleaning applied)
        df = pd.read_csv(input_file)

        # Convert 'Timestamp' to datetime
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')  # Invalid timestamps become NaT
        else:
            raise ValueError("Timestamp column not found in the dataset.")
        
        # Adjust the date for 7AM-7AM operational logic
        df['ShiftedDate'] = df['Timestamp'].apply(calculate_shifted_date)

    except Exception as e:
        print(f"Error reading or parsing the file: {e}")
        return

    # Ensure Timestamp is sorted
    df = df.sort_values('Timestamp')

    # Group by shifted date
    grouped = df.groupby('ShiftedDate')

    for shifted_date, group in grouped:
        if pd.isnull(shifted_date):
            print("Skipping rows with invalid timestamps.")
            continue  # Skip rows with invalid timestamps

        # Generate daily folder
        folder_name = os.path.join(output_base_dir, f"{shifted_date}_Office")
        os.makedirs(folder_name, exist_ok=True)

        # Generate clean file name
        filename = f"PUA_{shifted_date}_Office.csv"
        output_path = os.path.join(folder_name, sanitize_filename(filename))
        group.drop(columns=['ShiftedDate']).to_csv(output_path, index=False)
        print(f"Saved file: {output_path}")

def main():
    """
    Main program to interact with the user and split the CSV by daily data.
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
            # Split the file by day
            split_csv_by_day(input_file, output_base_dir)
        except Exception as e:
            print(f"An error occurred: {e}")
        
        another = input("Do you want to process another file? (y/n): ").strip().lower()
        if another != 'y':
            break

    print("Processing complete. Goodbye!")

if __name__ == "__main__":
    main()
