from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MetodoPago, Pago, HistorialPago

class HistorialPagoInline(admin.TabularInline):
    model = HistorialPago
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'fecha_cambio', 'ip_usuario')
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo', 'comision')
    list_filter = ('activo', 'tipo')
    search_fields = ('nombre',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('referencia', 'pedido', 'usuario', 'monto', 'metodo_pago', 'status', 'fecha_creacion')
    list_filter = ('status', 'metodo_pago', 'fecha_creacion')
    search_fields = ('referencia', 'pedido__id', 'usuario__username', 'usuario__email')
    readonly_fields = ('referencia', 'checksum', 'fecha_creacion', 'fecha_actualizacion')
    inlines = [HistorialPagoInline]
    
    def has_delete_permission(self, request, obj=None):
        # Prohibir eliminación de pagos para mantener integridad de auditoría
        return False
        
    def save_model(self, request, obj, form, change):
        """
        Sobrescribe el método save_model para registrar cambios de estado
        cuando se edita desde el admin.
        """
        if change and 'status' in form.changed_data:
            # Si se cambió el estado, crear una entrada en el historial
            HistorialPago.objects.create(
                pago=obj,
                estado_anterior=Pago.objects.get(pk=obj.pk).status,
                estado_nuevo=obj.status,
                ip_usuario=get_client_ip(request),
                notas=f"Cambio realizado por el administrador {request.user.username}"
            )
        super().save_model(request, obj, form, change)

@admin.register(HistorialPago)
class HistorialPagoAdmin(admin.ModelAdmin):
    list_display = ('pago', 'estado_anterior', 'estado_nuevo', 'fecha_cambio')
    list_filter = ('estado_nuevo', 'fecha_cambio')
    search_fields = ('pago__referencia', 'notas')
    readonly_fields = ('pago', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'ip_usuario')
    
    def has_add_permission(self, request):
        # No permitir añadir registros de historial manualmente
        return False
    
    def has_change_permission(self, request, obj=None):
        # No permitir modificar registros de historial
        return False
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar registros de historial
        return False

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