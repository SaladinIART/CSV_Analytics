import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
import io

def load_data(file_path):
    # Load CSV file and preprocess data
    df = pd.read_csv(file_path, parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    return df

def generate_statistical_summary(df):
    # Calculate and return statistical summary
    return df.describe()

def plot_time_series(df, columns):
    # Create time series plots for specified columns
    fig, axes = plt.subplots(len(columns), 1, figsize=(10, 4*len(columns)))
    for i, col in enumerate(columns):
        df[col].plot(ax=axes[i] if len(columns) > 1 else axes)
        (axes[i] if len(columns) > 1 else axes).set_title(col)
    plt.tight_layout()
    return fig

def create_correlation_heatmap(df):
    # Create correlation matrix and heatmap
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    return fig

def create_scatter_plot(df, x_col, y_col):
    # Create scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot.scatter(x=x_col, y=y_col, ax=ax)
    return fig

def figure_to_image(fig):
    # Convert matplotlib figure to ReportLab Image
    img_data = io.BytesIO()
    fig.savefig(img_data, format='png')
    img_data.seek(0)
    return Image(img_data)

def generate_pdf_report(output_file, stats, figures):
    # Generate PDF report using ReportLab
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Add statistical summary
    story.append(Paragraph("Statistical Summary", styles['Heading1']))
    data = [stats.reset_index().columns.tolist()] + stats.reset_index().values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(PageBreak())

    # Add figures
    for title, figure in figures.items():
        story.append(Paragraph(title, styles['Heading2']))
        img = figure_to_image(figure)
        img.drawHeight = 500
        img.drawWidth = 400
        story.append(img)
        story.append(PageBreak())

    doc.build(story)

def analyze_profile(input_file, output_dir):
    df = load_data(input_file)
    profile = os.path.splitext(os.path.basename(input_file))[0]
    profile_dir = os.path.join(output_dir, profile)
    os.makedirs(profile_dir, exist_ok=True)

    stats = generate_statistical_summary(df)
    
    figures = {
        "Time Series": plot_time_series(df, ['BILLET_TEMP', 'PROFILE_EXIT_TEMP', 'RAM_SPEED']),
        "Correlation Heatmap": create_correlation_heatmap(df),
        "Exit Temperature vs Ram Speed": create_scatter_plot(df, 'RAM_SPEED', 'PROFILE_EXIT_TEMP')
    }
    
    output_file = os.path.join(profile_dir, f"{profile}_analysis.pdf")
    generate_pdf_report(output_file, stats, figures)
    plt.close('all')  # Close all figures to free up memory
    
    print(f"Analysis complete. Report saved as: {output_file}")

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