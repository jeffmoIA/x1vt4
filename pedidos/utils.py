import os
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from django.shortcuts import get_object_or_404

from .models import Pedido

def generar_factura_pdf(pedido):
    """Genera una factura en PDF para un pedido"""
    # Crear un buffer para el PDF
    buffer = BytesIO()
    
    # Crear el objeto PDF usando ReportLab
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Establecer información básica
    p.setTitle(f"Factura - Pedido #{pedido.id}")
    
    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "MOTO TIENDA")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, "Factura / Recibo de compra")
    
    # Rectángulo para los datos de la factura
    p.rect(50, height - 150, width - 100, 70)
    
    # Datos de la factura
    p.setFont("Helvetica-Bold", 10)
    p.drawString(60, height - 95, f"PEDIDO #: {pedido.id}")
    p.drawString(60, height - 110, f"FECHA: {pedido.fecha_pedido.strftime('%d/%m/%Y')}")
    p.drawString(60, height - 125, f"CLIENTE: {pedido.nombre_completo}")
    
    # Datos de la empresa (en la parte derecha)
    p.drawString(350, height - 95, "MOTO TIENDA")
    p.setFont("Helvetica", 10)
    p.drawString(350, height - 110, "Dirección de la empresa")
    p.drawString(350, height - 125, "Teléfono: (123) 456-7890")
    p.drawString(350, height - 140, "Email: info@mototienda.com")
    
    # Dirección de envío
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 180, "DIRECCIÓN DE ENVÍO:")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 200, pedido.nombre_completo)
    direccion_lines = pedido.direccion.split('\n')
    y_position = height - 215
    for line in direccion_lines:
        p.drawString(50, y_position, line)
        y_position -= 15
    p.drawString(50, y_position, f"{pedido.ciudad}, {pedido.codigo_postal}")
    p.drawString(50, y_position - 15, f"Teléfono: {pedido.telefono}")
    
    # Tabla de productos
    data = [["PRODUCTO", "PRECIO", "CANT.", "SUBTOTAL"]]
    for item in pedido.items.all():
        data.append([
            item.producto.nombre,
            f"${item.precio}",
            str(item.cantidad),
            f"${item.precio_total()}"
        ])
    
    # Añadir fila de total
    data.append(["", "", "TOTAL", f"${pedido.total()}"])
    
    # Crear tabla
    table = Table(data, colWidths=[width*0.4, width*0.2, width*0.1, width*0.2])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('BOX', (0, -1), (-1, -1), 1, colors.black),
    ]))
    
    # Dibujar tabla
    table.wrapOn(p, width, height)
    table_height = len(data) * 20  # Altura aproximada
    table.drawOn(p, 50, height - 300 - table_height)
    
    # Pie de página
    p.setFont("Helvetica", 8)
    p.drawString(50, 30, "Esta factura sirve como comprobante de compra.")
    p.drawString(50, 15, f"Generada el {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Guardar PDF
    p.showPage()
    p.save()
    
    # Mover el cursor al principio del buffer y devolver el valor
    buffer.seek(0)
    return buffer

def obtener_factura(request, pedido_id):
    """Vista para descargar la factura de un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Generar el PDF
    buffer = generar_factura_pdf(pedido)
    
    # Crear la respuesta HTTP con el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_pedido_{pedido.id}.pdf"'
    response.write(buffer.getvalue())
    
    return response