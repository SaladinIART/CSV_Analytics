import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_outliers_isolation_forest(df, contamination=0.01):
    outliers = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for column in numeric_cols:
        X = df[[column]]
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outlier_labels = iso_forest.fit_predict(X)
        outliers[column] = df[column][outlier_labels == -1]
    
    return outliers

def summarize_outliers(outliers):
    summary = {}
    for column, outlier_series in outliers.items():
        summary[column] = {
            'count': len(outlier_series),
            'min': outlier_series.min() if len(outlier_series) > 0 else None,
            'max': outlier_series.max() if len(outlier_series) > 0 else None,
            'mean': outlier_series.mean() if len(outlier_series) > 0 else None
        }
    return summary

def get_outlier_timestamps(outliers):
    timestamps = {}
    for column, outlier_series in outliers.items():
        timestamps[column] = outlier_series.index.tolist()
    return timestamps