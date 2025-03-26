from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'  # Namespace para las URL de usuarios

urlpatterns = [
    # Ruta para la página de registro
    path('registro/', views.registro, name='registro'),
    
    # Ruta para la página de perfil (requiere autenticación)
    path('perfil/', views.perfil, name='perfil'),
    
    # Uso de las vistas de autenticación predeterminadas de Django
    # Vista de inicio de sesión con nuestra plantilla personalizada
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    
    # Vista de cierre de sesión que redirige a la página principal
    path('logout/', auth_views.LogoutView.as_view(next_page='tienda:inicio'), name='logout'),
]