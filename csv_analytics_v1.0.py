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

def load_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    return df

def generate_statistical_summary(df):
    summary = df.describe()
    summary.loc['range'] = summary.loc['max'] - summary.loc['min']
    return summary

def detect_outliers(df):
    outliers = {}
    for column in df.select_dtypes(include=['float64', 'int64']):
        z_scores = stats.zscore(df[column])
        outliers[column] = df[abs(z_scores) > 3][column]
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
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)

def generate_pdf_report(output_file, df, stats, figures, outliers):
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=1))
    story = []

    # Introduction
    story.append(Paragraph("Aluminum Extrusion Analysis Report", styles['Heading1']))
    story.append(Paragraph("This report provides an analysis of aluminum extrusion process data. It includes statistical summaries, time series analysis, correlation analysis, and identification of potential outliers.", styles['Justify']))
    story.append(Paragraph("Key Parameters:", styles['Heading2']))
    for param in df.columns:
        story.append(Paragraph(f"• {param}: Measured in {get_units(param)}", styles['BodyText']))
    story.append(PageBreak())

# Statistical Summary
    story.append(Paragraph("Statistical Summary", styles['Heading1']))
    data = [['Statistic'] + list(stats.columns)]
    for index, row in stats.iterrows():
        data.append([index] + [format_value(x) for x in row])
    table = Table(data)
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
    story.append(Paragraph("This table provides a statistical overview of the key parameters in the extrusion process. Pay attention to the mean values and ranges to understand typical operating conditions.", styles['Justify']))
    story.append(PageBreak())

    # Time Series
    story.append(Paragraph("Time Series Analysis", styles['Heading1']))
    story.append(figures['Time Series'])
    story.append(Paragraph("These time series plots show how key parameters vary over time. Look for trends, cycles, or sudden changes that might indicate process variations or issues.", styles['Justify']))
    story.append(PageBreak())

    # Correlation Heatmap
    story.append(Paragraph("Correlation Analysis", styles['Heading1']))
    story.append(figures['Correlation Heatmap'])
    story.append(Paragraph("The correlation heatmap shows relationships between different parameters. Strong positive correlations are shown in red, while strong negative correlations are in blue. This can help identify which parameters tend to change together.", styles['Justify']))
    story.append(PageBreak())

    # Scatter Plot
    story.append(Paragraph("Exit Temperature vs Ram Speed", styles['Heading1']))
    story.append(figures['Exit Temperature vs Ram Speed'])
    story.append(Paragraph("This scatter plot shows the relationship between the ram speed and the exit temperature. Any clear pattern here could indicate how adjusting the ram speed might affect the exit temperature of the extrusion.", styles['Justify']))
    story.append(PageBreak())

    # Outlier Analysis
    story.append(Paragraph("Outlier Analysis", styles['Heading1']))
    for param, values in outliers.items():
        if not values.empty:
            story.append(Paragraph(f"Potential outliers in {param}:", styles['Heading2']))
            outlier_data = [[str(index), f"{value:.2f}"] for index, value in values.items()]
            outlier_table = Table([['Timestamp', f'{param} ({get_units(param)})'] + outlier_data])
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
    story.append(Paragraph("Outliers are data points that are significantly different from other observations. They may indicate exceptional process conditions or potential measurement errors. These should be investigated to understand if they represent real events or data issues.", styles['Justify']))

    doc.build(story)

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M', errors='coerce')
    df.set_index('Date', inplace=True)
    return df

def analyze_profile(input_file, output_dir):
    try:
        df = load_data(input_file)
        profile = os.path.splitext(os.path.basename(input_file))[0]
        profile_dir = os.path.join(output_dir, profile)
        os.makedirs(profile_dir, exist_ok=True)

        stats = generate_statistical_summary(df)
        outliers = detect_outliers(df)
        
        figures = {
            "Time Series": figure_to_image(plot_time_series(df, ['BILLET_TEMP', 'PROFILE_EXIT_TEMP', 'RAM_SPEED', 'BREAKTHOUGH_PRESSURE'])),
            "Correlation Heatmap": figure_to_image(create_correlation_heatmap(df)),
            "Exit Temperature vs Ram Speed": figure_to_image(create_scatter_plot(df, 'RAM_SPEED', 'PROFILE_EXIT_TEMP'))
        }
        
        output_file = os.path.join(profile_dir, f"{profile}_analysis.pdf")
        generate_pdf_report(output_file, df, stats, figures, outliers)
        plt.close('all')  # Close all figures to free up memory
        
        print(f"Analysis complete. Report saved as: {output_file}")
    except Exception as e:
        print(f"An error occurred while analyzing the file: {str(e)}")

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