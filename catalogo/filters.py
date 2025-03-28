import django_filters
from django import forms
from .models import Producto, Categoria, Marca

class ProductoFilter(django_filters.FilterSet):
    """
    Filtro para el modelo Producto que permite filtrar por varios campos
    """
    # Filtro por nombre (contiene texto)
    nombre = django_filters.CharFilter(
        lookup_expr='icontains', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre...'})
    )
    
    # Filtro por precio (rango)
    precio_min = django_filters.NumberFilter(
        field_name='precio', 
        lookup_expr='gte',  # mayor o igual que
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Desde $'})
    )
    precio_max = django_filters.NumberFilter(
        field_name='precio', 
        lookup_expr='lte',  # menor o igual que
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Hasta $'})
    )
    
    # Filtro por categoría (múltiples opciones)
    categoria = django_filters.ModelMultipleChoiceFilter(
        queryset=Categoria.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
    # Filtro por marca (múltiples opciones)
    marca = django_filters.ModelMultipleChoiceFilter(
        queryset=Marca.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
    # Filtro por disponibilidad
    disponible = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,  # Importante: que no sea requerido
    )
    
    class Meta:
        model = Producto
        fields = ['nombre', 'precio_min', 'precio_max', 'categoria', 'marca', 'disponible']