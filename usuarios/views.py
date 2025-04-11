from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioFormSeguro, PerfilForm
from .models import Perfil

def registro(request):
    # Vista para el registro de nuevos usuarios
    if request.method == 'POST':
        # Si es una solicitud POST, procesar el formulario enviado
        form = RegistroUsuarioFormSeguro(request.POST)
        if form.is_valid():
            # Guardar el usuario si los datos son válidos
            user = form.save()
            # Crear un perfil asociado al nuevo usuario
            Perfil.objects.create(usuario=user)
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            # Redirigir a la página principal
            return redirect('tienda:inicio')
    else:
        # Si es una solicitud GET, mostrar el formulario vacío
        form = RegistroUsuarioFormSeguro()
    # Renderizar la plantilla con el formulario
    return render(request, 'usuarios/registro.html', {'form': form})

@login_required  # Decorador que asegura que solo usuarios autenticados accedan
def perfil(request):
    # Vista para ver y editar el perfil de usuario
    # Obtener el perfil del usuario actual
    perfil = Perfil.objects.get(usuario=request.user)
    
    if request.method == 'POST':
        # Si es POST, procesar el formulario de actualización
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            # Guardar los cambios si son válidos
            form.save()
            # Redirigir a la misma página para ver los cambios
            return redirect('usuarios:perfil')
    else:
        # Si es GET, mostrar el formulario con los datos actuales
        form = PerfilForm(instance=perfil)
        
    # Renderizar la plantilla con el formulario
    return render(request, 'usuarios/perfil.html', {'form': form})