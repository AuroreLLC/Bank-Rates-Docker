from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
import pandas as pd
from datetime import datetime

def generate_pdf_from_df(df: pd.DataFrame, title: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, title)

    c.setFont("Helvetica", 10)
    y = height - 80
    line_height = 18

    # Estimate column widths
    col_widths = []
    for col in df.columns:
        max_text = max([str(x) for x in df[col]] + [col], key=len)
        col_width = stringWidth(max_text, "Helvetica", 10) + 20
        col_widths.append(col_width)

    x_positions = [40]
    for w in col_widths[:-1]:
        x_positions.append(x_positions[-1] + w)

    # Draw header
    for i, col in enumerate(df.columns):
        c.drawString(x_positions[i], y, str(col))
    y -= line_height

    # Draw data rows
    for _, row in df.iterrows():
        for i, val in enumerate(row):
            c.drawString(x_positions[i], y, str(val))
        y -= line_height
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
            for i, col in enumerate(df.columns):
                c.drawString(x_positions[i], y, str(col))
            y -= line_height

    # Signature section
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Authorized Signatures:")
    y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(40, y, "Name:")
    c.line(90, y, 300, y)
    y -= 30
    c.drawString(40, y, "Title:")
    c.line(90, y, 300, y)
    y -= 30
    c.drawString(40, y, "Signature:")
    c.line(100, y, 300, y)
    y -= 30
    c.drawString(40, y, "Date:")
    c.line(80, y, 200, y)

    # Footer with timestamp
    timestamp = datetime.now().strftime("Generated on: %Y-%m-%d %H:%M:%S")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(40, 30, timestamp)

    c.save()
    buffer.seek(0)
    return buffer
