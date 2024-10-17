import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import io
from scipy import stats
import numpy as np
import argparse
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator

def load_data(file_path):
    df = pd.read_csv(file_path)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y %H:%M')
        df.set_index('Date', inplace=True)
    return df

def generate_statistical_summary(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = df[numeric_cols].describe()
    summary.loc['range'] = summary.loc['max'] - summary.loc['min']
    return summary

def detect_outliers(df, threshold=3):
    outliers = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for column in numeric_cols:
        z_scores = np.abs(stats.zscore(df[column]))
        outliers[column] = df[column][z_scores > threshold]
    return outliers

def plot_time_series(df, columns):
    available_columns = [col for col in columns if col in df.columns and np.issubdtype(df[col].dtype, np.number)]
    figures = []
    
    for col in available_columns:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 18), gridspec_kw={'height_ratios': [2, 1]})
        
        # Full range plot
        df[col].plot(ax=ax1)
        format_axis(ax1, col)
        
        # Focused plot (only for temperature-related columns)
        if 'TEMP' in col:
            df[col].plot(ax=ax2)
            format_axis(ax2, col)
            ax2.set_ylim(450, 550)  # Set y-axis limits to focus on the range around 500°C
            ax2.set_title(f"{col} (Focused on 500°C Range)")
        else:
            fig.delaxes(ax2)  # Remove the second subplot if it's not a temperature column
            
        plt.tight_layout()
        figures.append((f"{col} Over Time", fig))
    
    return figures

def format_axis(ax, col):
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    if 'TEMP' in col:
        ax.axhline(y=500, color='orange', linestyle=':', linewidth=2)
    
    ax.set_title(col)
    ax.set_ylabel(get_units(col))
    ax.set_xlabel('Time')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
def create_correlation_heatmap(df):
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return None
    
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt='.2f')
    ax.set_title("Correlation Heatmap")
    plt.tight_layout()
    return fig

def create_scatter_plot(df, x_col, y_col):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df[x_col], df[y_col], alpha=0.5)
    ax.set_xlabel(f"{x_col} ({get_units(x_col)})")
    ax.set_ylabel(f"{y_col} ({get_units(y_col)})")
    ax.set_title(f"{y_col} vs {x_col}")
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

def create_extrusion_pressure_plot(df):
    pressure_columns = ['BREAKTHOUGH_PRESSURE', 'MAIN_RAM_PRESSURE']
    available_columns = [col for col in pressure_columns if col in df.columns and np.issubdtype(df[col].dtype, np.number)]
    
    if not available_columns:
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in available_columns:
        ax.plot(df.index, df[col], label=col)
    ax.set_xlabel('Time')
    ax.set_ylabel('Pressure (MPa)')
    ax.set_title('Extrusion Pressure Over Time')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def generate_pdf_report(output_file, df, stats, figures, outliers):
    doc = SimpleDocTemplate(output_file, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()

    # Introduction
    story.append(Paragraph("Aluminum Extrusion Analysis Report", styles['Heading1']))
    report_date = df.index[0].strftime("%Y-%m-%d")
    story.append(Paragraph(f"This report provides an analysis of aluminum extrusion process data for machine P7 on {report_date}.", styles['BodyText']))
    
    # Data Structure
    story.append(Paragraph("Data Structure", styles['Heading2']))
    story.append(Paragraph(f"Number of rows: {len(df)}", styles['BodyText']))
    story.append(Paragraph(f"Number of columns: {len(df.columns)}", styles['BodyText']))
    story.append(Paragraph("Columns:", styles['BodyText']))
    for col in df.columns:
        story.append(Paragraph(f"• {col}: {df[col].dtype}", styles['BodyText']))
    story.append(PageBreak())

    # Statistical Summary
    story.append(Paragraph("Statistical Summary", styles['Heading2']))
    stats_columns = list(stats.columns)
    first_half = stats_columns[:4]
    second_half = stats_columns[4:]

    for half in [first_half, second_half]:
        data = [['Statistic'] + half]
        data.extend(stats[half].reset_index().values.tolist())
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Paragraph("", styles['Normal']))  # Add some space between tables

    story.append(PageBreak())

    # Figures
    for title, fig in figures:
        story.append(Paragraph(title, styles['Heading2']))
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
        img_data.seek(0)
        img = Image(img_data)
        
        # Calculate the available space on the page
        available_width = doc.width * 0.9  # 90% of the page width
        available_height = doc.height * 0.7  # 70% of the page height
        
        # Adjust the image size to fit within the available space
        img.drawWidth = available_width
        img.drawHeight = available_height
        aspect = img.imageWidth / float(img.imageHeight)
        if img.drawWidth / float(img.drawHeight) > aspect:
            img.drawWidth = img.drawHeight * aspect
        else:
            img.drawHeight = img.drawWidth / aspect
        
        story.append(img)
        story.append(PageBreak())

    # Outlier Analysis
    story.append(Paragraph("Outlier Analysis", styles['Heading2']))
    for col, values in outliers.items():
        if not values.empty:
            story.append(Paragraph(f"Outliers in {col}:", styles['Heading3']))
            data = [['Timestamp', f'{col} ({get_units(col)})']]
            data.extend(values.reset_index().values.tolist())
            t = Table(data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
            story.append(PageBreak())
            
    doc.build(story)

def create_extrusion_pressure_plot(df):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches
    ax.plot(df.index, df['BREAKTHOUGH_PRESSURE'], label='Breakthrough Pressure')
    ax.plot(df.index, df['MAIN_RAM_PRESSURE'], label='Main Ram Pressure')
    ax.set_xlabel('Time')
    ax.set_ylabel('Pressure (MPa)')
    ax.set_title('Extrusion Pressure Over Time')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def analyze_profile(input_file, output_dir):
    df = load_data(input_file)
    # Exclude specified columns
    df = df.drop(['DATE_ID', 'EXT_TIME', 'DEAD_CYCLE_TIME', 'BILLET_COUNTER'], axis=1, errors='ignore')
    
    profile = os.path.splitext(os.path.basename(input_file))[0]
    profile_dir = os.path.join(output_dir, profile)
    os.makedirs(profile_dir, exist_ok=True)

    stats = generate_statistical_summary(df)
    outliers = detect_outliers(df)
    
    time_series_figures = plot_time_series(df, df.select_dtypes(include=[np.number]).columns)
    
    figures = time_series_figures + [
        ("Extrusion Pressure Over Time", create_extrusion_pressure_plot(df)),
        ("Correlation Heatmap", create_correlation_heatmap(df))
    ]
    
    output_file = os.path.join(profile_dir, f"{profile}_analysis.pdf")
    generate_pdf_report(output_file, df, stats, figures, outliers)
    plt.close('all')  # Close all figures to free up memory

    print(f"Analysis complete. Report saved as: {output_file}")

# Main execution code remains the same

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