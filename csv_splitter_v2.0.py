import csv
import os
from collections import defaultdict
import datetime

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def sanitize_filename(filename):
    # Replace slashes with hyphens and remove any other invalid characters
    return ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in filename.replace('/', '-'))

def split_csv_by_profile_and_date(input_file, output_base_dir):
    # Columns to exclude
    exclude_columns = ['DATE_ID', 'DEAD_CYCLE_TIME']

    # Dictionary to store data for each profile and date
    profile_date_data = defaultdict(lambda: defaultdict(list))

    # Read the input CSV file
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Filter out the excluded columns
        fieldnames = [field for field in reader.fieldnames if field not in exclude_columns]

        for row in reader:
            profile = row['PROFILE']
            date_str = row['Date'].split()[0]  # Extract date part from Date column
            
            # Store the row data
            filtered_row = {k: v for k, v in row.items() if k in fieldnames}
            profile_date_data[profile][date_str].append(filtered_row)

    # Write data to separate CSV files
    for profile, date_data in profile_date_data.items():
        for date_str, rows in date_data.items():
            sanitized_profile = sanitize_filename(profile)
            sanitized_date = sanitize_filename(date_str)
            
            profile_dir = os.path.join(output_base_dir, 'by_profile', sanitized_profile)
            date_dir = os.path.join(output_base_dir, 'by_date', sanitized_date)
            
            os.makedirs(profile_dir, exist_ok=True)
            os.makedirs(date_dir, exist_ok=True)
            
            profile_file = os.path.join(profile_dir, f"{sanitized_profile}_{sanitized_date}.csv")
            date_file = os.path.join(date_dir, f"{sanitized_profile}_{sanitized_date}.csv")
            
            # Write to profile-specific file
            with open(profile_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            # Write to date-specific file
            with open(date_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

    print(f"Split CSV files based on {len(profile_date_data)} profiles and their respective dates.")

    # Generate key notes
    generate_key_notes(profile_date_data, output_base_dir)

def generate_key_notes(profile_date_data, output_base_dir):
    key_notes = []

    for profile, date_data in profile_date_data.items():
        for date_str, rows in date_data.items():
            num_records = len(rows)
            key_notes.append(f"Profile: {profile}, Date: {date_str}, Number of records: {num_records}")

    # Get current date for the filename
    current_date = get_current_date()
    
    # Write key notes to a file with the current date in the filename
    key_notes_file = os.path.join(output_base_dir, f'key_notes_{current_date}.txt')
    with open(key_notes_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(key_notes))

    print(f"Key notes have been written to {key_notes_file}")
    
# Usage
input_file = r"D:\Csv analytics\csv_data_to_analyze\p7_16_10_24.csv"
output_base_dir = r"D:\Csv analytics\csv_data_to_analyze\output"

try:
    split_csv_by_profile_and_date(input_file, output_base_dir)
except Exception as e:
    print(f"An error occurred: {str(e)}")
    print("Please check that the input file exists and the output directory is writable.")