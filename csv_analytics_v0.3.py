import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import io
from scipy import stats
import traceback
import numpy as np

def load_data(file_path):
    df = pd.read_csv(file_path)
    print("Columns in the CSV file:", df.columns.tolist())
    print("\nSample data:")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
    
    # Convert 'Date' column to datetime if it exists
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M', errors='coerce')
        df.set_index('Date', inplace=True)
    
    # Convert numeric columns to float, ignoring non-numeric values
    numeric_columns = ['BILLET_TEMP', 'BREAKTHOUGH_PRESSURE', 'PROFILE_EXIT_TEMP', 'RAM_SPEED', 'EXT_TIME', 'MAIN_RAM_PRESSURE']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def generate_statistical_summary(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = df[numeric_cols].describe()
    summary.loc['range'] = summary.loc['max'] - summary.loc['min']
    return summary

def detect_outliers(df):
    outliers = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for column in numeric_cols:
        z_scores = stats.zscore(df[column].dropna())
        outliers[column] = df[column][abs(z_scores) > 3]
    return outliers

def plot_time_series(df, columns):
    fig, axes = plt.subplots(len(columns), 1, figsize=(10, 4*len(columns)))
    for i, col in enumerate(columns):
        ax = axes[i] if len(columns) > 1 else axes
        df[col].plot(ax=ax)
        ax.set_title(col)
        ax.set_ylabel(get_units(col))
    plt.tight_layout()
    return fig

def create_correlation_heatmap(df):
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt='.2f')
    ax.set_title("Correlation Heatmap")
    return fig

def create_scatter_plot(df, x_col, y_col):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot.scatter(x=x_col, y=y_col, ax=ax)
    ax.set_xlabel(f"{x_col} ({get_units(x_col)})")
    ax.set_ylabel(f"{y_col} ({get_units(y_col)})")
    ax.set_title(f"{y_col} vs {x_col}")
    return fig

def figure_to_image(fig):
    img_data = io.BytesIO()
    fig.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
    img_data.seek(0)
    return Image(img_data, width=6*inch, height=4*inch)

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

def format_value(value):
    if isinstance(value, pd.Series):
        return value.apply(format_value)
    if pd.isna(value):
        return "N/A"
    elif isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)

def create_table(data):
    formatted_data = [[format_value(cell) for cell in row] for row in data]
    return Table(formatted_data)

def generate_pdf_report(output_file, df, stats, figures, outliers):
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=1))
    story = []

    # Introduction
    story.append(Paragraph("Aluminum Extrusion Analysis Report", styles['Heading1']))
    story.append(Paragraph("This report provides an analysis of aluminum extrusion process data.", styles['Justify']))
    
    # Data Structure Information
    story.append(Paragraph("Data Structure", styles['Heading2']))
    story.append(Paragraph(f"Number of rows: {len(df)}", styles['BodyText']))
    story.append(Paragraph(f"Number of columns: {len(df.columns)}", styles['BodyText']))
    story.append(Paragraph("Columns:", styles['BodyText']))
    for col in df.columns:
        story.append(Paragraph(f"• {col}: {df[col].dtype}", styles['BodyText']))
    story.append(PageBreak())

    # Statistical Summary
    story.append(Paragraph("Statistical Summary", styles['Heading1']))
    summary_data = [['Statistic'] + list(stats.columns)]
    for index, row in stats.iterrows():
        summary_data.append([index] + [format_value(x) for x in row])
    
    table = create_table(summary_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Paragraph("This table provides a statistical overview of the key parameters in the extrusion process.", styles['Justify']))
    story.append(PageBreak())

    # Figures
    for title, figure in figures.items():
        story.append(Paragraph(title, styles['Heading2']))
        story.append(figure)
        story.append(PageBreak())

    # Outliers
    story.append(Paragraph("Outlier Analysis", styles['Heading2']))
    for param, values in outliers.items():
        if not values.empty:
            story.append(Paragraph(f"Potential outliers in {param}:", styles['Heading3']))
            outlier_data = [[index, format_value(value)] for index, value in values.items()]
            outlier_table = create_table([['Timestamp', f'{param} ({get_units(param)})']] + outlier_data)
            outlier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(outlier_table)
    try:
        doc.build(story)
        print(f"PDF report generated successfully: {output_file}")
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        print(traceback.format_exc())

def analyze_profile(input_file, output_dir):
    try:
        df = load_data(input_file)
        profile = os.path.splitext(os.path.basename(input_file))[0]
        profile_dir = os.path.join(output_dir, profile)
        os.makedirs(profile_dir, exist_ok=True)

        print("Generating statistical summary...")
        stats = generate_statistical_summary(df)
        print("Detecting outliers...")
        outliers = detect_outliers(df)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        time_series_cols = [col for col in ['BILLET_TEMP', 'PROFILE_EXIT_TEMP', 'RAM_SPEED', 'BREAKTHOUGH_PRESSURE'] if col in numeric_cols]
        
        print("Creating figures...")
        figures = {
            "Time Series": figure_to_image(plot_time_series(df, time_series_cols)),
            "Correlation Heatmap": figure_to_image(create_correlation_heatmap(df[numeric_cols])),
            "Exit Temperature vs Ram Speed": figure_to_image(create_scatter_plot(df, 'RAM_SPEED', 'PROFILE_EXIT_TEMP'))
        }
        
        output_file = os.path.join(profile_dir, f"{profile}_analysis.pdf")
        print(f"Generating PDF report: {output_file}")
        generate_pdf_report(output_file, df, stats, figures, outliers)
        plt.close('all')  # Close all figures to free up memory
        
        print(f"Analysis complete. Report saved as: {output_file}")
    except Exception as e:
        print(f"An error occurred while analyzing the file: {str(e)}")
        print("Detailed error information:")
        print(traceback.format_exc())

def main(output_dir):
    while True:
        input_file = input("Please enter the full path of the CSV file you want to analyze (or 'q' to quit): ").strip()
        
        if input_file.lower() == 'q':
            break
        
        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist. Please try again.")
            continue
        
        if not input_file.endswith('.csv'):
            print("Error: Please select a CSV file.")
            continue
        
        analyze_profile(input_file, output_dir)
        
        another = input("Do you want to analyze another file? (y/n): ").strip().lower()
        if another != 'y':
            break

    print("Analysis complete. Goodbye!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze aluminum extrusion data")
    parser.add_argument("--output_dir", default="D:\\Csv analytics\\analysis_output", help="Path to output directory")
    args = parser.parse_args()

    main(args.output_dir)