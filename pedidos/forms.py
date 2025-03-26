from django import forms
from .models import Pedido

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