from django import forms
from .models import Pedido
from core.utils import sanitize_input

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_completo', 'direccion', 'ciudad', 'codigo_postal', 'telefono', 'notas']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instrucciones especiales para la entrega (opcional)'}),
        }
        
    def clean_nombre_completo(self):
        nombre_completo = self.cleaned_data.get('nombre_completo')
        return sanitize_input(nombre_completo)
        
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        return sanitize_input(direccion)
        
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')
        return sanitize_input(ciudad)
        
    def clean_codigo_postal(self):
        codigo_postal = self.cleaned_data.get('codigo_postal')
        return sanitize_input(codigo_postal)
        
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        return sanitize_input(telefono)
        
    def clean_notas(self):
        notas = self.cleaned_data.get('notas')
        return sanitize_html(notas) # Permitimos HTML básico en las notas