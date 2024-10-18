import pandas as pd
import numpy as np
import os

def load_data(file_path):
    df = pd.read_csv(file_path)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y %H:%M')
        df.set_index('Date', inplace=True)
    return df

def preprocess_data(df):
    # Handle missing values
    df = df.interpolate()
    
    # Smooth noisy data using rolling mean
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].rolling(window=5, center=True, min_periods=1).mean()
    
    return df

def verify_file_format(file_path):
    file_name = os.path.basename(file_path)
    if not file_name.endswith('.csv'):
        return False
    
    # Extract the date part from the filename
    date_part = file_name.split('.')[0]  # Remove .csv
    date_range = date_part.split('_to_')
    
    if len(date_range) != 2:
        return False
    
    try:
        pd.to_datetime(date_range[0], format='%Y-%m-%d')
        pd.to_datetime(date_range[1], format='%Y-%m-%d')
    except ValueError:
        return False
    
    return True