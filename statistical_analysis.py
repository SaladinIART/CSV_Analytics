import pandas as pd
import numpy as np

def generate_statistical_summary(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = df[numeric_cols].describe()
    summary.loc['range'] = summary.loc['max'] - summary.loc['min']
    return summary

def calculate_correlations(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corr()
    return correlations

def calculate_daily_stats(df):
    daily_stats = df.resample('D').agg(['mean', 'min', 'max', 'std'])
    return daily_stats

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