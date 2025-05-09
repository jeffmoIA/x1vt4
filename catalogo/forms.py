from django import forms
from django.forms import inlineformset_factory
from .models import Producto, TallaProducto, ImagenProducto
from core.utils import sanitize_input, sanitize_html

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'marca', 
                 'stock', 'disponible']
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
    
    def clean_nombre(self):
        """Sanitiza el nombre del producto."""
        nombre = self.cleaned_data.get('nombre')
        return sanitize_input(nombre)
    
    def clean_descripcion(self):
        """Sanitiza la descripción permitiendo HTML básico seguro."""
        descripcion = self.cleaned_data.get('descripcion')
        return sanitize_html(descripcion)

# Definición del formset para tallas
TallaFormSet = inlineformset_factory(
    Producto, TallaProducto, 
    fields=('talla', 'disponible', 'stock'),
    extra=1,  # Añade un formulario vacío para nuevas tallas
    can_delete=True,
    min_num=0,
    validate_min=False,
    max_num=15,
    validate_max=True,
    widgets={
        'talla': forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ej: S, M, L, XL, 42, 44'
        }),
        'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'stock': forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0',
            'placeholder': 'Cantidad disponible'
        }),
    }
)

# Formset para imágenes
# Formset para imágenes optimizado con mejor manejo de eliminación
ImagenFormSet = inlineformset_factory(
    Producto, ImagenProducto,
    fields=('imagen', 'titulo', 'orden', 'es_principal'),
    extra=0,  # Cambiamos de 1 a 0 para que no añada formularios extra automáticamente
    can_delete=True,
    max_num=10,  # Máximo 10 imágenes
    validate_max=True,
    widgets={
        'imagen': forms.FileInput(attrs={
            'class': 'form-control', 
            'accept': 'image/*'
        }),
        'titulo': forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Título descriptivo de la imagen'
        }),
        'orden': forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '1',
            'value': '1'
        }),
        'es_principal': forms.CheckboxInput(attrs={
            'class': 'principal-checkbox'
        }),
    }
)


