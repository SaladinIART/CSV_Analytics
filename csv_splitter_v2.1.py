import csv
import os
from collections import defaultdict
import datetime
from datetime import timedelta
import pandas as pd 

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def sanitize_filename(filename):
    return ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in filename.replace('/', '-'))

def split_csv_by_profile_and_date(input_file, output_base_dir):
    exclude_columns = ['DATE_ID', 'DEAD_CYCLE_TIME']
    profile_date_data = defaultdict(lambda: defaultdict(list))

    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = [field for field in reader.fieldnames if field not in exclude_columns]

        for row in reader:
            profile = row['PROFILE']
            date_str = row['Date'].split()[0]
            filtered_row = {k: v for k, v in row.items() if k in fieldnames}
            profile_date_data[profile][date_str].append(filtered_row)

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
            
            for file_path in [profile_file, date_file]:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

    print(f"Split CSV files based on {len(profile_date_data)} profiles and their respective dates.")
    generate_key_notes(profile_date_data, output_base_dir)

def split_csv_by_day(input_file, output_base_dir):
    df = pd.read_csv(input_file, parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    
    def get_day_group(date):
        if date.hour < 7:
            return (date - timedelta(days=1)).strftime('%Y-%m-%d')
        return date.strftime('%Y-%m-%d')
    
    df['day_group'] = df.index.map(get_day_group)
    
    for day, group in df.groupby('day_group'):
        start_date = datetime.datetime.strptime(day, '%Y-%m-%d') + timedelta(hours=7)
        end_date = start_date + timedelta(days=1)
        filename = f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.csv"
        output_path = os.path.join(output_base_dir, 'by_day', filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        group.to_csv(output_path)
        print(f"Saved file: {output_path}")

def generate_key_notes(profile_date_data, output_base_dir):
    key_notes = []
    for profile, date_data in profile_date_data.items():
        for date_str, rows in date_data.items():
            num_records = len(rows)
            key_notes.append(f"Profile: {profile}, Date: {date_str}, Number of records: {num_records}")

    current_date = get_current_date()
    key_notes_file = os.path.join(output_base_dir, f'key_notes_{current_date}.txt')
    with open(key_notes_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(key_notes))

    print(f"Key notes have been written to {key_notes_file}")

def main():
    output_base_dir = r"D:\Csv analytics\csv_data_to_analyze\output"

    while True:
        input_file = input("Please enter the full path of the CSV file you want to split (or 'q' to quit): ").strip()
        
        if input_file.lower() == 'q':
            break
        
        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist. Please try again.")
            continue
        
        if not input_file.endswith('.csv'):
            print("Error: Please select a CSV file.")
            continue
        
        split_method = input("Do you want to split by day (7AM to 7AM) or by profile and date? Enter 'day' or 'profile': ").strip().lower()
        
        try:
            if split_method == 'day':
                split_csv_by_day(input_file, output_base_dir)
            elif split_method == 'profile':
                split_csv_by_profile_and_date(input_file, output_base_dir)
            else:
                print("Invalid option. Please enter 'day' or 'profile'.")
                continue
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please check that the input file exists and the output directory is writable.")
        
        another = input("Do you want to split another file? (y/n): ").strip().lower()
        if another != 'y':
            break

    print("CSV splitting complete. Goodbye!")

if __name__ == "__main__":
    main()