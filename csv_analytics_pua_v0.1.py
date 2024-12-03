import pandas as pd
import matplotlib.pyplot as plt

# Define TNB cost rate (example: 0.355 RM/kWh)
COST_RATE = 0.355  # Update this based on your actual rates

# Load the CSV file
file_path = r"D:\OneDrive\Desktop\rx380_daily_logs\p7_pua.csv"  # Replace with your actual path
data = pd.read_csv(file_path)

# Convert timestamp to datetime with proper dayfirst handling
data['timestamp'] = pd.to_datetime(data['timestamp'], dayfirst=True)

# Convert total_real_energy to numeric
data['total_real_energy'] = pd.to_numeric(data['total_real_energy'], errors='coerce')

# Replace NaN values in total_real_energy with 0
data['total_real_energy'].fillna(0, inplace=True)

# Calculate cost per hour
data['cost_per_hour'] = data['total_real_energy'] * COST_RATE

# Visualization: Cost Per Hour
plt.figure(figsize=(12, 6))
plt.plot(data['timestamp'], data['cost_per_hour'], label='Cost per Hour (RM)')
plt.title("Cost Per Hour Trend")
plt.xlabel("Timestamp")
plt.ylabel("Cost (RM)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Visualization: Peak Demand
plt.figure(figsize=(12, 6))
plt.plot(data['timestamp'], data['total_real_power'], label='Peak Demand (kW)', color='orange')
plt.title("Peak Demand Trend")
plt.xlabel("Timestamp")
plt.ylabel("Demand (kW)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Combined Dashboard: Key Metrics
fig, ax = plt.subplots(2, 2, figsize=(16, 12))

# Subplot 1: Voltage Trends
ax[0, 0].plot(data['timestamp'], data['voltage_l1'], label='Voltage L1', alpha=0.7)
ax[0, 0].plot(data['timestamp'], data['voltage_l2'], label='Voltage L2', alpha=0.7)
ax[0, 0].plot(data['timestamp'], data['voltage_l3'], label='Voltage L3', alpha=0.7)
ax[0, 0].set_title("Voltage Trends")
ax[0, 0].set_xlabel("Timestamp")
ax[0, 0].set_ylabel("Voltage (V)")
ax[0, 0].legend()
ax[0, 0].grid(True)

# Subplot 2: Current Trends
if 'current_l1' in data.columns:
    ax[0, 1].plot(data['timestamp'], data['current_l1'], label='Current L1', alpha=0.7)
    ax[0, 1].plot(data['timestamp'], data['current_l2'], label='Current L2', alpha=0.7)
    ax[0, 1].plot(data['timestamp'], data['current_l3'], label='Current L3', alpha=0.7)
    ax[0, 1].set_title("Current Trends")
    ax[0, 1].set_xlabel("Timestamp")
    ax[0, 1].set_ylabel("Current (A)")
    ax[0, 1].legend()
    ax[0, 1].grid(True)

# Subplot 3: Power Factor
if 'total_power_factor' in data.columns:
    ax[1, 0].plot(data['timestamp'], data['total_power_factor'], label='Power Factor', color='green')
    ax[1, 0].set_title("Power Factor Trend")
    ax[1, 0].set_xlabel("Timestamp")
    ax[1, 0].set_ylabel("Power Factor")
    ax[1, 0].grid(True)
    ax[1, 0].legend()

# Subplot 4: Cost per Hour
ax[1, 1].plot(data['timestamp'], data['cost_per_hour'], label='Cost per Hour (RM)', color='purple')
ax[1, 1].set_title("Cost Per Hour")
ax[1, 1].set_xlabel("Timestamp")
ax[1, 1].set_ylabel("Cost (RM)")
ax[1, 1].grid(True)
ax[1, 1].legend()

plt.tight_layout()
plt.show()