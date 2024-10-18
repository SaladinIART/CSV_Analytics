import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator

def plot_time_series(df, columns):
    available_columns = [col for col in columns if col in df.columns and np.issubdtype(df[col].dtype, np.number)]
    figures = []
    
    for col in available_columns:
        fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches
        df[col].plot(ax=ax)
        format_axis(ax, col)
        plt.tight_layout()
        figures.append((f"{col} Over Time", fig))
    
    return figures

def format_axis(ax, col):
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    ax.set_title(col)
    ax.set_ylabel(get_units(col))
    ax.set_xlabel('Time')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

def create_combined_pressure_plot(df):
    fig, ax1 = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches
    
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Pressure (MPa)', color='tab:blue')
    ax1.plot(df.index, df['MAIN_RAM_PRESSURE'], color='tab:blue', label='Main Ram Pressure')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Pump Values', color='tab:orange')
    ax2.plot(df.index, df['MAIN_PUMP_2'], color='tab:orange', label='Main Pump 2')
    ax2.plot(df.index, df['MAIN_PUMP_3'], color='tab:green', label='Main Pump 3')
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    
    fig.tight_layout()
    plt.title('Combined Pressure and Pump Values Over Time')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    
    return fig

def create_correlation_heatmap(df):
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt='.2f')
    ax.set_title("Correlation Heatmap")
    plt.tight_layout()
    return fig

def get_units(parameter):
    units = {
        'BILLET_TEMP': '°C',
        'PROFILE_EXIT_TEMP': '°C',
        'RAM_SPEED': 'mm/s',
        'EXT_TIME': 's',
        'BREAKTHOUGH_PRESSURE': 'MPa',
        'MAIN_RAM_PRESSURE': 'MPa'
    }
    return units.get(parameter, '')