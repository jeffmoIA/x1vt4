from django.contrib import admin
from .models import Pedido, ItemPedido, HistorialEstadoPedido

class HistorialEstadoInline(admin.TabularInline):
    model = HistorialEstadoPedido
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario', 'notas')
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ('producto', 'precio', 'cantidad')
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nombre_completo', 'fecha_pedido', 'estado', 'pagado', 'total_pedido')
    list_filter = ('estado', 'pagado', 'fecha_pedido')
    search_fields = ('id', 'usuario__username', 'nombre_completo', 'email')
    readonly_fields = ('fecha_pedido',)
    inlines = [ItemPedidoInline, HistorialEstadoInline]
    fieldsets = (
        ('Información básica', {
            'fields': ('usuario', 'fecha_pedido', 'estado', 'pagado')
        }),
        ('Información de contacto', {
            'fields': ('nombre_completo', 'direccion', 'ciudad', 'codigo_postal', 'telefono')
        }),
        ('Información de pago', {
            'fields': ('metodo_pago', 'referencia_pago')
        }),
        ('Información de envío', {
            'fields': ('empresa_envio', 'codigo_seguimiento', 'fecha_envio', 'fecha_entrega')
        }),
        ('Notas', {
            'fields': ('notas', 'notas_admin')
        }),
    )
    
    def total_pedido(self, obj):
        return f"${obj.total()}"
    total_pedido.short_description = 'Total'
    
    def save_model(self, request, obj, form, change):
        # Si el estado ha cambiado, registrar el cambio
        if change and 'estado' in form.changed_data:
            estado_anterior = Pedido.objects.get(pk=obj.pk).estado
            HistorialEstadoPedido.objects.create(
                pedido=obj,
                estado_anterior=estado_anterior,
                estado_nuevo=obj.estado,
                usuario=request.user,
                notas=f"Cambio realizado por el administrador {request.user.username}"
            )
        super().save_model(request, obj, form, change)

@admin.register(HistorialEstadoPedido)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario')
    list_filter = ('estado_nuevo', 'fecha_cambio')
    search_fields = ('pedido__id', 'usuario__username')
    readonly_fields = ('pedido', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario', 'notas')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False