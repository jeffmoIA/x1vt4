from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    raw_id_fields = ['producto']
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'nombre_completo', 'fecha_pedido', 'pagado', 'estado']
    list_filter = ['pagado', 'estado', 'fecha_pedido']
    search_fields = ['nombre_completo', 'usuario__username']
    inlines = [ItemPedidoInline]
    list_editable = ['estado', 'pagado']