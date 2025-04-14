from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Dice hola'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('¡Hola! El sistema de comandos funciona.'))