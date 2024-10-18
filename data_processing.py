import pandas as pd
import numpy as np
import os

def load_data(file_path):
    df = pd.read_csv(file_path)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.set_index('Date', inplace=True)
    return df

def preprocess_data(df):
    # Convert object columns to numeric where possible
    for col in df.select_dtypes(include=['object']):
        try:
            df[col] = pd.to_numeric(df[col])
        except ValueError:
            pass  # Keep as object if conversion fails
    
    # Handle missing values
    df = df.infer_objects(copy=False)  # Infer better dtypes before interpolation
    numeric_df = df.select_dtypes(include=[np.number])
    df[numeric_df.columns] = numeric_df.interpolate()
    
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