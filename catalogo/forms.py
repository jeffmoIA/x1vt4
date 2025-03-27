from django import forms
from django.forms import inlineformset_factory
from .models import Producto, TallaProducto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'marca', 
                 'stock', 'disponible', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

# Definición del formset para tallas
TallaFormSet = inlineformset_factory(
    Producto, TallaProducto, 
    fields=('talla', 'disponible', 'stock'),
    extra=3,
    can_delete=True,
    widgets={
        'talla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: S, M, 42, 54'}),
        'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
    }
)