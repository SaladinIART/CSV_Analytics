import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

# Define TNB cost rate (example: 0.355 RM/kWh)
COST_RATE = 0.355

def log_error(message):
    """Log errors to a file with a timestamp."""
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"{pd.Timestamp.now()} - {message}\n")

def validate_columns(data, required_columns):
    """Validate that all required columns are present."""
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        log_error(f"Missing columns: {', '.join(missing_columns)}")
        return False
    return True

def main():
    # Prompt user for file path
    file_path = input("Enter the path to the filtered .csv file: ").strip()
    
    if not os.path.exists(file_path):
        log_error(f"File not found: {file_path}")
        print("Error: File not found. Check the path and try again.")
        return
    
    try:
        # Load the data
        data = pd.read_csv(file_path)
    except Exception as e:
        log_error(f"Failed to read file {file_path}: {str(e)}")
        print("Error: Unable to read the file. Check the format and try again.")
        return

    # Validate required columns
    required_columns = ['timestamp', 'total_real_energy', 'total_real_power']
    if not validate_columns(data, required_columns):
        print("Error: Missing required columns. Check the error log for details.")
        return

    # Convert timestamp to datetime and energy to numeric
    try:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['total_real_energy'] = pd.to_numeric(data['total_real_energy'], errors='coerce')
    except Exception as e:
        log_error(f"Data parsing error: {str(e)}")
        print("Error: Failed to parse data. Check the error log for details.")
        return

    # Fill missing energy values with 0
    data['total_real_energy'].fillna(0, inplace=True)

    # Calculate cost per hour
    data['cost_per_hour'] = data['total_real_energy'] * COST_RATE

    # Generate the PDF report
    pdf_filename = "Energy_Report.pdf"
    with PdfPages(pdf_filename) as pdf:
        # Page 1: Cost Per Hour Trend
        plt.figure(figsize=(12, 6))
        plt.plot(data['timestamp'], data['cost_per_hour'], label='Cost per Hour (RM)', color='blue')
        plt.title("Cost Per Hour Trend")
        plt.xlabel("Timestamp")
        plt.ylabel("Cost (RM)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # Page 2: Peak Demand Trend
        plt.figure(figsize=(12, 6))
        plt.plot(data['timestamp'], data['total_real_power'], label='Peak Demand (kW)', color='orange')
        plt.title("Peak Demand Trend")
        plt.xlabel("Timestamp")
        plt.ylabel("Demand (kW)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # Page 3: Summary Table
        total_energy = data['total_real_energy'].sum()
        total_cost = data['cost_per_hour'].sum()
        peak_demand = data['total_real_power'].max()
        avg_cost_per_hour = data['cost_per_hour'].mean()
        missing_data_points = data['total_real_energy'].isna().sum()
        summary_text = f"""
        Energy Monitoring Report:

        - Total Energy Consumption (kWh): {total_energy:,.2f}
        - Total Cost (RM): {total_cost:,.2f}
        - Peak Demand Observed (kW): {peak_demand:,.2f}
        - Average Cost per Hour (RM): {avg_cost_per_hour:,.2f}

        Data Issues:
        - Missing Data Points: {missing_data_points}
        """
        plt.figure(figsize=(8.5, 11))
        plt.text(0.1, 0.9, summary_text, fontsize=12, va='top', wrap=True)
        plt.axis('off')
        pdf.savefig()
        plt.close()

    print(f"Report successfully saved as {pdf_filename}")

if __name__ == "__main__":
    main()
