import csv
import os
from collections import defaultdict

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
            profile_dir = os.path.join(output_base_dir, 'by_profile', profile)
            date_dir = os.path.join(output_base_dir, 'by_date', date_str)
            
            os.makedirs(profile_dir, exist_ok=True)
            os.makedirs(date_dir, exist_ok=True)
            
            profile_file = os.path.join(profile_dir, f"{profile}_{date_str}.csv")
            date_file = os.path.join(date_dir, f"{profile}_{date_str}.csv")
            
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

    # Write key notes to a file
    key_notes_file = os.path.join(output_base_dir, 'key_notes.txt')
    with open(key_notes_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(key_notes))

    print(f"Key notes have been written to {key_notes_file}")

# Usage
input_file = r"D:\Csv analytics\csv_data_to_analyze\p7_10_24.csv"
output_base_dir = r"D:\Csv analytics\csv_data_to_analyze\output"

split_csv_by_profile_and_date(input_file, output_base_dir)