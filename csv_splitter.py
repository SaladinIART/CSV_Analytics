import csv
import os

def split_csv_by_profile(input_file, output_base_dir):
    # Columns to exclude
    exclude_columns = ['DATE_ID', 'DECELERATION_PRESSURE', 'DEAD_CYCLE_TIME', 'PILOT_PRESSURE', 'CONTAINER_SEAL_PRESSURE', 'MAIN_PUMP_2', 'MAIN_PUMP_3']

    # Dictionary to store file handlers for each profile
    profile_files = {}
    profile_writers = {}

    # Read the input CSV file
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Filter out the excluded columns
        fieldnames = [field for field in reader.fieldnames if field not in exclude_columns]

        for row in reader:
            profile = row['PROFILE']
            
            # Create a new directory and file for the profile if it doesn't exist
            if profile not in profile_files:
                profile_dir = os.path.join(output_base_dir, profile)
                os.makedirs(profile_dir, exist_ok=True)
                
                output_file = os.path.join(profile_dir, f"{profile}.csv")
                profile_files[profile] = open(output_file, 'w', newline='', encoding='utf-8')
                
                profile_writers[profile] = csv.DictWriter(profile_files[profile], fieldnames=fieldnames)
                profile_writers[profile].writeheader()
            
            # Write the row to the corresponding profile's CSV file, excluding specified columns
            filtered_row = {k: v for k, v in row.items() if k in fieldnames}
            profile_writers[profile].writerow(filtered_row)

    # Close all open file handlers
    for file in profile_files.values():
        file.close()

    print(f"Split CSV files based on {len(profile_files)} profiles, excluding specified columns.")

# Usage
input_file = r"D:\Csv analytics\csv_data_to_analyze\p7_10_24.csv"
output_base_dir = r"D:\Csv analytics\csv_data_to_analyze"

split_csv_by_profile(input_file, output_base_dir)