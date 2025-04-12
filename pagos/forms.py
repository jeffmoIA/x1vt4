from django import forms
from .models import Pago, MetodoPago
from core.utils import sanitize_input
import re
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger('mototienda.security')

class TarjetaForm(forms.Form):
    """
    Formulario para procesar pagos con tarjeta.
    No almacena datos sensibles de tarjetas conforme a PCI DSS.
    """
    titular = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del titular como aparece en la tarjeta'
        })
    )
    
    numero_tarjeta = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'autocomplete': 'cc-number',  # Atributo para navegadores
            'data-mask': '0000 0000 0000 0000'  # Para usar con scripts de máscara
        })
    )
    
    fecha_expiracion = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'autocomplete': 'cc-exp',
            'data-mask': '00/00'
        })
    )
    
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV',
            'autocomplete': 'cc-csc',
            'data-mask': '000'
        })
    )
    
    guardar_tarjeta = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_titular(self):
        """Valida y sanitiza el nombre del titular."""
        titular = self.cleaned_data.get('titular', '')
        return sanitize_input(titular)
    
    def clean_numero_tarjeta(self):
        """Valida y formatea el número de tarjeta."""
        numero = self.cleaned_data.get('numero_tarjeta', '')
        # Eliminar espacios y guiones
        numero = re.sub(r'[\s-]', '', numero)
        
        # Verificar que solo contiene dígitos
        if not numero.isdigit():
            raise forms.ValidationError("El número de tarjeta debe contener solo dígitos.")
            
        # Verificar longitud válida (13-19 dígitos según estándares)
        if not (13 <= len(numero) <= 19):
            raise forms.ValidationError("Longitud de número de tarjeta inválida.")
            
        # Algoritmo de Luhn (validación básica de tarjetas)
        if not self._luhn_check(numero):
            logger.warning(f"Intento de pago con número de tarjeta que no pasa validación Luhn")
            raise forms.ValidationError("Número de tarjeta inválido.")
            
        return numero
    
    def clean_fecha_expiracion(self):
        """Valida que la fecha de expiración sea correcta y esté en el futuro."""
        fecha = self.cleaned_data.get('fecha_expiracion', '')
        
        # Verificar formato (MM/YY)
        if not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', fecha):
            raise forms.ValidationError("Formato inválido. Use MM/YY (ej: 12/25)")
            
        try:
            mes, anio = fecha.split('/')
            mes = int(mes)
            anio = int(f"20{anio}")  # Convertir a formato completo
            
            # Verificar que la fecha no está expirada
            hoy = timezone.now()
            
            if anio < hoy.year or (anio == hoy.year and mes < hoy.month):
                logger.warning(f"Intento de pago con tarjeta expirada: {fecha}")
                raise forms.ValidationError("La tarjeta ha expirado.")
                
        except (ValueError, IndexError):
            raise forms.ValidationError("Fecha de expiración inválida")
            
        return fecha
    
    def clean_cvv(self):
        """Valida el código de seguridad (CVV)."""
        cvv = self.cleaned_data.get('cvv', '')
        
        # Eliminar espacios
        cvv = cvv.strip()
        
        # Verificar que solo contiene dígitos
        if not cvv.isdigit():
            raise forms.ValidationError("El CVV debe contener solo dígitos.")
            
        # Verificar longitud (3-4 dígitos dependiendo del tipo de tarjeta)
        if not (3 <= len(cvv) <= 4):
            raise forms.ValidationError("Longitud de CVV inválida.")
            
        return cvv
    
    def _luhn_check(self, card_number):
        """
        Implementa el algoritmo de Luhn para validar números de tarjeta.
        
        Args:
            card_number (str): Número de tarjeta sin espacios ni guiones
            
        Returns:
            bool: True si el número es válido según el algoritmo
        """
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]  # Dígitos en posiciones impares desde la derecha
        even_digits = digits[-2::-2]  # Dígitos en posiciones pares desde la derecha
        
        # Suma de dígitos impares
        total = sum(odd_digits)
        
        # Suma de dígitos pares (duplicados y sumados sus dígitos si > 9)
        for d in even_digits:
            d *= 2
            # Si el resultado tiene dos dígitos, sumar esos dígitos
            if d > 9:
                d = d - 9  # Equivalente a sumar los dígitos (ej: 14 → 1+4 = 5, también 14-9 = 5)
            total += d
            
        # El número es válido si el total es múltiplo de 10
        return total % 10 == 0

class TransferenciaForm(forms.Form):
    """Formulario para registrar pagos por transferencia bancaria."""
    nombre_ordenante = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de quien realiza la transferencia'
        })
    )
    
    banco_origen = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Banco desde el que se realiza la transferencia'
        })
    )
    
    def clean_nombre_ordenante(self):
        nombre = self.cleaned_data.get('nombre_ordenante', '')
        return sanitize_input(nombre)
        
    def clean_banco_origen(self):
        banco = self.cleaned_data.get('banco_origen', '')
        return sanitize_input(banco)

class MetodoPagoSeleccionForm(forms.Form):
    """Formulario para seleccionar el método de pago."""
    metodo_pago = forms.ModelChoiceField(
        queryset=MetodoPago.objects.filter(activo=True),
        empty_label=None,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )