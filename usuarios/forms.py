from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class RegistroUsuarioForm(UserCreationForm):
    # Extendemos el formulario de creación de usuario predeterminado de Django
    email = forms.EmailField(required=True)  # Hacemos que el email sea obligatorio
    
    class Meta:
        model = User  # Usamos el modelo User de Django
        # Campos que mostraremos en el formulario
        fields = ('username', 'email', 'password1', 'password2')
        
class PerfilForm(forms.ModelForm):
    # Formulario para editar el perfil del usuario
    class Meta:
        model = Perfil  # Usamos nuestro modelo Perfil
        # Campos que podrá editar el usuario
        fields = ('telefono', 'direccion', 'ciudad', 'codigo_postal')