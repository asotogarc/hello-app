import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_from_last_csv_row(csv_file, pdf_file):
    # Leer la última fila del CSV
    with open(csv_file, 'r') as file:
        csv_reader = list(csv.reader(file))
        last_row = csv_reader[-1]

    # Extraer datos
    from_who, to_who, logo, num_invoice, date_invoice, due_date, items, notes, term = last_row

     # Crear PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=30, bottomMargin=30)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    # Título y datos principales
    elements.append(Paragraph(f"Factura #{num_invoice}", title_style))
    elements.append(Paragraph(f"De: {from_who}", normal_style))
    elements.append(Paragraph(f"Para: {to_who}", normal_style))
    elements.append(Paragraph(f"Fecha: {date_invoice}", normal_style))
    elements.append(Paragraph(f"Fecha de vencimiento: {due_date}", normal_style))

    # Condiciones de pago

    # Tabla de items
    items_data = eval(items)
    table_data = [['Artículo', 'Cantidad', 'Precio', 'Total']]
    subtotal = 0
    for item in items_data:
        row = [item['Articulo'], item['Cantidad'], f"€{item['Precio']:.2f}", f"€{item['Total']:.2f}"]
        table_data.append(row)
        subtotal += item['Total']

    table = Table(table_data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)

    # Resumen financiero
    tax_rate = 0.21  # Asume un 21% de IVA, ajusta según sea necesario
    discount_rate = 0.05  # Asume un 5% de descuento, ajusta según sea necesario
    tax = subtotal * tax_rate
    discount = subtotal * discount_rate
    total = subtotal + tax - discount

    financial_data = [
        ['Subtotal', f"€{subtotal:.2f}"],
        ['Impuesto (21%)', f"€{tax:.2f}"],
        ['Descuento (50%)', f"€{discount:.2f}"],
        ['Total', f"€{total:.2f}"]
    ]

    financial_table = Table(financial_data, colWidths=[300, 200])
    financial_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, -1), (-1, -1), 6),
    ]))

    elements.append(financial_table)

    # Notas y términos
    elements.append(Paragraph("Notas:", subtitle_style))
    elements.append(Paragraph(notes, normal_style))


    elements.append(Paragraph("Términos:", subtitle_style))
    elements.append(Paragraph(term, normal_style))

    
    # Generar PDF
    doc.build(elements)

    return pdf_file
