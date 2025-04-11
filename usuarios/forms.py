from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Perfil
from core.utils import sanitize_input, sanitize_html

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado de inicio de sesión con mensaje de error genérico
    para prevenir enumeración de usuarios.
    """
    error_messages = {
        'invalid_login': "Por favor, introduce un nombre de usuario y contraseña correctos. "
                         "Ten en cuenta que ambos campos pueden ser sensibles a mayúsculas.",
        'inactive': "Esta cuenta está inactiva.",
    }
    
    # Configura clases para Bootstrap
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    
    def clean_username(self):
        """Sanitiza el nombre de usuario."""
        username = self.cleaned_data.get('username')
        return sanitize_input(username)

class RegistroUsuarioFormSeguro(UserCreationForm):
    """
    Formulario de registro con validaciones adicionales de seguridad.
    """
    email = forms.EmailField(required=True)  # Email obligatorio
    
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="<ul>"
                  "<li>Tu contraseña no puede ser similar a tu información personal</li>"
                  "<li>Tu contraseña debe contener al menos 10 caracteres</li>"
                  "<li>Tu contraseña no puede ser una contraseña de uso común</li>"
                  "<li>Tu contraseña no puede ser completamente numérica</li>"
                  "</ul>",
    )
    
    password2 = forms.CharField(
        label="Confirma contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text="Introduce la misma contraseña que antes, para verificación.",
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Verifica que el email no exista ya en la base de datos."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email
    
    def clean_username(self):
        """Sanitiza el nombre de usuario."""
        username = self.cleaned_data.get('username')
        return sanitize_input(username)
    
    def clean_email(self):
        """Sanitiza y verifica que el email no exista ya en la base de datos."""
        email = self.cleaned_data.get('email')
        sanitized_email = sanitize_input(email)
        if User.objects.filter(email=sanitized_email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return sanitized_email

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ('telefono', 'direccion', 'ciudad', 'codigo_postal')
        
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        return sanitize_input(telefono)
        
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        return sanitize_input(direccion)
        
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')
        return sanitize_input(ciudad)
        
    def clean_codigo_postal(self):
        codigo_postal = self.cleaned_data.get('codigo_postal')
        return sanitize_input(codigo_postal)