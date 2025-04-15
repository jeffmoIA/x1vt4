from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear un perfil cuando se crea un usuario nuevo"""
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar el perfil cuando se guarda un usuario"""
    try:
        instance.perfil.save()
    except Perfil.DoesNotExist:
        # Si el perfil no existe, crearlo
        Perfil.objects.create(usuario=instance)