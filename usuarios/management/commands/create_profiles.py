from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import Perfil

class Command(BaseCommand):
    help = 'Crea perfiles para usuarios que no los tienen'
    
    def handle(self, *args, **options):
        # Contar usuarios sin perfil
        count = 0
        
        # Iterar sobre todos los usuarios
        for user in User.objects.all():
            try:
                # Intentar acceder al perfil
                _ = user.perfil
            except Perfil.DoesNotExist:
                # Si no existe, crear uno
                Perfil.objects.create(usuario=user)
                count += 1
                self.stdout.write(f"Creado perfil para {user.username}")
        
        self.stdout.write(self.style.SUCCESS(f"Se crearon {count} perfiles"))