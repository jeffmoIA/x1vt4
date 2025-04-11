from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name = 'usuarios'  # Namespace para las URL de usuarios

urlpatterns = [
    # Ruta para la página de registro
    path('registro/', views.registro, name='registro'),
    
    # Ruta para la página de perfil (requiere autenticación)
    path('perfil/', views.perfil, name='perfil'),
    
    # Vista de inicio de sesión con nuestro formulario personalizado
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html',
        authentication_form=LoginForm
    ), name='login'),
    
    # Vista de cierre de sesión que redirige a la página principal
    path('logout/', auth_views.LogoutView.as_view(next_page='tienda:inicio'), name='logout'),
    
    # Rutas para gestión de contraseñas
    path('cambiar-password/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/cambiar_password.html',
        success_url='/usuarios/password-cambiado/'
    ), name='cambiar_password'),
    
    path('password-cambiado/', auth_views.PasswordChangeDoneView.as_view(
        template_name='usuarios/password_cambiado.html'
    ), name='password_cambiado'),
]