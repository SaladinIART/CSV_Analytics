from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import matplotlib.pyplot as plt

def generate_pdf_report(output_file, df, stats, figures, outliers, correlations):
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
    story.extend(create_table_from_dataframe(stats, "Statistical Summary"))
    story.append(PageBreak())

    # Correlation Matrix
    story.append(Paragraph("Correlation Matrix", styles['Heading2']))
    story.extend(create_table_from_dataframe(correlations, "Correlation Matrix"))
    story.append(PageBreak())

    # Figures
    for title, fig in figures:
        story.append(Paragraph(title, styles['Heading2']))
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
        img_data.seek(0)
        img = Image(img_data)
        img.drawWidth = 7.5 * inch
        img.drawHeight = 5 * inch
        story.append(img)
        story.append(PageBreak())

    # Outlier Analysis
    story.append(Paragraph("Outlier Analysis", styles['Heading2']))
    for col, values in outliers.items():
        if not values.empty:
            story.append(Paragraph(f"Outliers in {col}:", styles['Heading3']))
            story.extend(create_table_from_dataframe(values.reset_index(), f"Outliers in {col}"))
            story.append(PageBreak())
            
    doc.build(story)

def create_table_from_dataframe(df, title):
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return [Paragraph(title, getSampleStyleSheet()['Heading3']), table]