from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.urls import reverse
from django.views import View

from .models import Pago, MetodoPago, HistorialPago
from .forms import TarjetaForm, TransferenciaForm, MetodoPagoSeleccionForm
from .services import PaymentProcessor
from pedidos.models import Pedido

import logging
import json

logger = logging.getLogger('mototienda.security')

@login_required
def seleccionar_metodo_pago(request, pedido_id):
    """
    Vista para seleccionar el método de pago para un pedido.
    
    Args:
        request: HttpRequest
        pedido_id: ID del pedido a pagar
        
    Returns:
        HttpResponse
    """
    # Obtener el pedido o retornar 404
    pedido = get_object_or_404(
        Pedido.objects.select_related('usuario'),
        id=pedido_id, 
        usuario=request.user,
        estado='pendiente',  # Solo se pueden pagar pedidos pendientes
        pagado=False  # Y que no estén pagados
    )
    
    # Si el pedido ya tiene un pago en proceso, redirigir a ese pago
    pago_existente = Pago.objects.filter(
        pedido=pedido,
        status__in=['pendiente', 'procesando']
    ).first()
    
    if pago_existente:
        return redirect('pagos:procesar_pago', pago_id=pago_existente.id)
    
    # Procesar el formulario si es POST
    if request.method == 'POST':
        form = MetodoPagoSeleccionForm(request.POST)
        if form.is_valid():
            metodo_pago = form.cleaned_data['metodo_pago']
            
            # Crear un nuevo registro de pago
            with transaction.atomic():
                pago = Pago.objects.create(
                    pedido=pedido,
                    usuario=request.user,
                    metodo_pago=metodo_pago,
                    monto=pedido.total(),
                    gateway_usado='simulado'  # Esto cambiaría en producción
                )
                
                # Crear la primera entrada en el historial
                HistorialPago.objects.create(
                    pago=pago,
                    estado_anterior='',
                    estado_nuevo='pendiente',
                    ip_usuario=get_client_ip(request)
                )
            
            # Redirigir al procesamiento específico según el método
            return redirect('pagos:procesar_pago', pago_id=pago.id)
    else:
        form = MetodoPagoSeleccionForm()
    
    return render(request, 'pagos/seleccionar_metodo.html', {
        'form': form,
        'pedido': pedido
    })

@login_required
def procesar_pago(request, pago_id):
    """
    Vista para procesar un pago según el método seleccionado.
    
    Args:
        request: HttpRequest
        pago_id: ID del pago a procesar
        
    Returns:
        HttpResponse
    """
    # Obtener el pago o retornar 404
    pago = get_object_or_404(
        Pago.objects.select_related('pedido', 'metodo_pago'),
        id=pago_id,
        usuario=request.user,
        status__in=['pendiente', 'procesando']  # Solo pagos no finalizados
    )
    
    # Verificar integridad para pagos existentes
    if pago.checksum and not pago.verify_integrity():
        logger.error(f"Posible manipulación detectada en pago {pago.id}")
        messages.error(request, "Se ha detectado un problema con este pago. Por favor, contacte a soporte.")
        return redirect('pedidos:lista_pedidos')
    
    # Obtener el formulario adecuado según el método de pago
    metodo = pago.metodo_pago.tipo
    form = None
    template = None
    
    if metodo == 'tarjeta':
        form_class = TarjetaForm
        template = 'pagos/tarjeta.html'
    elif metodo == 'transferencia':
        form_class = TransferenciaForm
        template = 'pagos/transferencia.html'
    elif metodo == 'paypal':
        # Para PayPal redirigimos a otra vista que maneja la integración
        return redirect('pagos:paypal_redirect', pago_id=pago.id)
    elif metodo == 'efectivo':
        # Para efectivo simplemente confirmamos el pedido
        pago.status = 'pendiente'
        pago.save()
        pago.pedido.pagado = True  # Marcar como pagado (se pagará al entregar)
        pago.pedido.metodo_pago = "Efectivo"
        pago.pedido.save()
        messages.success(request, "Pedido confirmado. Pagarás al recibir tu pedido.")
        return redirect('pedidos:detalle_pedido', pedido_id=pago.pedido.id)
    else:
        messages.error(request, "Método de pago no soportado")
        return redirect('pagos:seleccionar_metodo_pago', pedido_id=pago.pedido.id)
    
    # Procesar el formulario si es POST
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            # Obtener datos del procesador de pago correspondiente
            processor = PaymentProcessor.get_processor(metodo)
            
            # Preparar datos para el procesador (específicos para cada método)
            payment_data = {
                'monto': pago.monto,
                'pedido': pago.pedido,
                'usuario': request.user
            }
            
            # Añadir datos específicos según el método
            if metodo == 'tarjeta':
                payment_data.update({
                    'card_number': form.cleaned_data['numero_tarjeta'],
                    'card_expiry': form.cleaned_data['fecha_expiracion'],
                    'cvv': form.cleaned_data['cvv'],
                    'card_holder': form.cleaned_data['titular']
                })
            elif metodo == 'transferencia':
                payment_data.update({
                    'nombre_ordenante': form.cleaned_data['nombre_ordenante'],
                    'banco_origen': form.cleaned_data['banco_origen']
                })
            
            # Procesar el pago
            success, message, transaction_id = processor.process_payment(payment_data)
            
            # Actualizar el estado del pago
            pago.status = 'completado' if success else 'fallido'
            pago.transaccion_id = transaction_id if transaction_id else ''
            pago.save()
            
            # Si el pago es exitoso, actualizar el pedido
            if success:
                pago.pedido.pagado = True
                pago.pedido.referencia_pago = transaction_id
                pago.pedido.metodo_pago = pago.metodo_pago.nombre
                pago.pedido.save()
                
                # Si el método es 'transferencia', cambiar estado a procesando
                if metodo == 'transferencia':
                    pago.pedido.cambiar_estado('procesando', 'Pedido pagado por transferencia')
                
                messages.success(request, f"Pago procesado correctamente. {message}")
                return redirect('pedidos:detalle_pedido', pedido_id=pago.pedido.id)
            else:
                messages.error(request, f"Error en el pago: {message}")
    else:
        form = form_class()
    
    return render(request, template, {
        'form': form,
        'pago': pago,
        'pedido': pago.pedido
    })

@login_required
def resumen_pago(request, pago_id):
    """
    Vista para mostrar el resumen de un pago completado.
    
    Args:
        request: HttpRequest
        pago_id: ID del pago
        
    Returns:
        HttpResponse
    """
    # Obtener el pago o retornar 404
    pago = get_object_or_404(
        Pago.objects.select_related('pedido', 'metodo_pago'),
        id=pago_id,
        usuario=request.user
    )
    
    return render(request, 'pagos/resumen.html', {
        'pago': pago,
        'pedido': pago.pedido
    })

@method_decorator(login_required, name='dispatch')
class PayPalRedirectView(View):
    """Vista para manejar la redirección a PayPal y callback."""
    
    def get(self, request, pago_id):
        """Maneja la redirección inicial a PayPal."""
        pago = get_object_or_404(
            Pago.objects.select_related('pedido'),
            id=pago_id,
            usuario=request.user,
            status__in=['pendiente', 'procesando']
        )
        
        # En un sistema real, aquí se generaría la URL de PayPal
        # y se redireccionaría al usuario
        
        # Para este simulador, simplemente mostramos una página
        return render(request, 'pagos/paypal_redirect.html', {
            'pago': pago,
            'pedido': pago.pedido
        })
    
    def post(self, request, pago_id):
        """Procesa la respuesta del pago PayPal (simulado)."""
        pago = get_object_or_404(
            Pago.objects.select_related('pedido'),
            id=pago_id,
            usuario=request.user,
            status__in=['pendiente', 'procesando']
        )
        
        # Procesar el pago con PayPal
        processor = PaymentProcessor.get_processor('paypal')
        payment_data = {
            'monto': pago.monto,
            'pedido': pago.pedido,
            'usuario': request.user,
            'paypal_email': request.user.email
        }
        
        success, message, transaction_id = processor.process_payment(payment_data)
        
        # Actualizar estado del pago
        pago.status = 'completado' if success else 'fallido'
        pago.transaccion_id = transaction_id if transaction_id else ''
        pago.save()
        
        if success:
            pago.pedido.pagado = True
            pago.pedido.referencia_pago = transaction_id
            pago.pedido.metodo_pago = "PayPal"
            pago.pedido.save()
            messages.success(request, "Pago por PayPal completado correctamente")
            return redirect('pedidos:detalle_pedido', pedido_id=pago.pedido.id)
        else:
            messages.error(request, f"Error en el pago por PayPal: {message}")
            return redirect('pagos:seleccionar_metodo_pago', pedido_id=pago.pedido.id)

# Función auxiliar para obtener la IP del cliente
def get_client_ip(request):
    """
    Obtiene la dirección IP real del cliente.
    
    Args:
        request: HttpRequest
        
    Returns:
        str: Dirección IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip