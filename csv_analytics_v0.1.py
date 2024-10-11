import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def load_data(file_path):
    return pd.read_csv(file_path, parse_dates=['Date'])

def create_output_folder(output_prefix):
    # Create a folder using the output prefix
    if not os.path.exists(output_prefix):
        os.makedirs(output_prefix)
    return output_prefix

def preprocess_data(df):
    df['DATE_ID'] = pd.to_datetime(df['DATE_ID'], format='%Y%m%d')
    return df

def calculate_statistics(df):
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    stats = df[numeric_columns].agg(['mean', 'median', 'std', 'min', 'max'])
    return stats

def identify_outliers(df, columns, threshold=3):
    outliers = {}
    for column in columns:
        z_scores = (df[column] - df[column].mean()) / df[column].std()
        outliers[column] = df[abs(z_scores) > threshold]
    return outliers

def plot_time_series(df, columns, output_file):
    plt.figure(figsize=(12, 6))
    for column in columns:
        plt.plot(df['Date'], df[column], label=column)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Time Series Plot')
    plt.legend()
    plt.savefig(output_file)
    plt.close()

def plot_correlation_heatmap(df, output_file):
    # Select only numeric columns for correlation
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    
    # Now plot the correlation heatmap only for numeric columns
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
    plt.savefig(output_file)
    plt.close()

def perform_pca(df):
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[numeric_columns])
    pca = PCA()
    pca_result = pca.fit_transform(scaled_data)
    return pca, pca_result

def plot_pca(pca, pca_result, output_file):
    plt.figure(figsize=(10, 8))
    plt.scatter(pca_result[:, 0], pca_result[:, 1])
    plt.xlabel('First Principal Component')
    plt.ylabel('Second Principal Component')
    plt.title('PCA Result')
    plt.savefig(output_file)
    plt.close()

def perform_clustering(df, n_clusters=3):
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[numeric_columns])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(scaled_data)
    return cluster_labels

def plot_clusters(df, cluster_labels, output_file):
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(df['BILLET_TEMP'], df['PROFILE_EXIT_TEMP'], c=cluster_labels, cmap='viridis')
    plt.xlabel('BILLET_TEMP')
    plt.ylabel('PROFILE_EXIT_TEMP')
    plt.title('K-means Clustering Result')
    plt.colorbar(scatter)
    plt.savefig(output_file)
    plt.close()

def generate_pdf_report(stats, outliers, output_file):
    # Create PDF document with A4 page size
    pdf = SimpleDocTemplate(output_file, pagesize=A4)

    elements = []

    # Define column widths to fit A4 width
    column_widths = [1.2 * inch] * len(stats.columns)

    # Convert DataFrame to list of lists
    data = [stats.columns.to_list()] + stats.values.tolist()

    # Create Table with column widths and data
    table = Table(data, colWidths=column_widths)

    # Apply style to the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add the table to the elements
    elements.append(table)

    # Build the PDF
    pdf.build(elements)

def main(input_file, output_prefix):
    # Create the output folder
    output_folder = create_output_folder(output_prefix)
    
    df = load_data(input_file)
    df = preprocess_data(df)
    
    # Calculate statistics and identify outliers
    stats = calculate_statistics(df)
    outliers = identify_outliers(df, ['BILLET_TEMP', 'BREAKTHOUGH_PRESSURE', 'PROFILE_EXIT_TEMP', 'RAM_SPEED'])
    
    # Generate visualizations
    plot_time_series(df, ['BILLET_TEMP', 'PROFILE_EXIT_TEMP', 'RAM_SPEED'], f'{output_folder}/time_series.png')
    plot_correlation_heatmap(df, f'{output_folder}/correlation_heatmap.png')
    
    # Perform PCA
    pca, pca_result = perform_pca(df)
    plot_pca(pca, pca_result, f'{output_folder}/pca.png')
    
    # Perform clustering
    cluster_labels = perform_clustering(df)
    plot_clusters(df, cluster_labels, f'{output_folder}/clusters.png')
    
    # Generate PDF report
    generate_pdf_report(stats, outliers, f'{output_folder}/report.pdf')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze aluminum extrusion data")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_prefix", help="Prefix for output files")
    args = parser.parse_args()

    main(args.input_file, args.output_prefix)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze aluminum extrusion data")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_prefix", help="Prefix for output files")
    args = parser.parse_args()

    main(args.input_file, args.output_prefix)