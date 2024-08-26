import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_from_last_csv_row(csv_file, pdf_file):
    # Leer la última fila del CSV (sin cambios)
    try:
        with open(csv_file, 'r', encoding='iso-8859-1') as file:
            csv_reader = list(csv.reader(file))
            last_row = csv_reader[-1]
    except UnicodeDecodeError:
        with open(csv_file, 'r', encoding='iso-8859-1') as file:
            csv_reader = list(csv.reader(file))
            last_row = csv_reader[-1]
    
    # Extraer datos
    from_who, to_who, logo, num_invoice, date_invoice, due_date, items, notes, term, tax_rate_str, discount_rate_str = last_row
    
    # Crear PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []

    # Estilos mejorados
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=12, textColor=colors.darkblue)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=14, spaceBefore=6, spaceAfter=6, textColor=colors.darkblue)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, spaceBefore=3, spaceAfter=3)
    
    # Título y datos principales
    elements.append(Paragraph(f"Factura #{num_invoice}", title_style))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"<b>De:</b> {from_who}", normal_style))
    elements.append(Paragraph(f"<b>Para:</b> {to_who}", normal_style))
    elements.append(Paragraph(f"<b>Fecha:</b> {date_invoice}", normal_style))
    elements.append(Paragraph(f"<b>Fecha de vencimiento:</b> {due_date}", normal_style))
    elements.append(Spacer(1, 0.25*inch))

    # Tabla de items
    items_data = eval(items)
    table_data = [['Artículo', 'Cantidad', 'Precio', 'Total']]
    subtotal = 0
    for item in items_data:
        row = [item['Articulo'], item['Cantidad'], f"€{item['Precio']:.2f}", f"€{item['Total']:.2f}"]
        table_data.append(row)
        subtotal += item['Total']
    
    table = Table(table_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.25*inch))

    # Resumen financiero
    tax_rate = float(tax_rate_str)
    discount_rate = float(discount_rate_str)
    tax = subtotal * tax_rate
    discount = subtotal * discount_rate
    total = subtotal + tax - discount
    financial_data = [
        ['Subtotal', f"€{subtotal:.2f}"],
        ['Impuesto', f"€{tax:.2f}"],
        ['Descuento', f"€{discount:.2f}"],
        ['Total', f"€{total:.2f}"]
    ]
    financial_table = Table(financial_data, colWidths=[4*inch, 2*inch])
    financial_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, -1), (-1, -1), 6),
    ]))
    elements.append(financial_table)
    elements.append(Spacer(1, 0.5*inch))

    # Notas y términos
    elements.append(Paragraph("Notas:", subtitle_style))
    elements.append(Paragraph(notes, normal_style))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("Términos:", subtitle_style))
    elements.append(Paragraph(term, normal_style))
    
    # Generar PDF
    doc.build(elements)
    return pdf_file
