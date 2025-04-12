from django.core.management.base import BaseCommand
from pagos.models import MetodoPago

class Command(BaseCommand):
    help = 'Crea los métodos de pago predeterminados para la tienda'
    
    def handle(self, *args, **options):
        # Lista de métodos de pago a crear
        metodos = [
            {
                'nombre': 'Tarjeta de Crédito/Débito',
                'tipo': 'tarjeta',
                'descripcion': 'Pago seguro con tarjeta de crédito o débito.',
                'comision': 0.0,
            },
            {
                'nombre': 'Transferencia Bancaria',
                'tipo': 'transferencia',
                'descripcion': 'Realiza una transferencia bancaria a nuestra cuenta.',
                'comision': 0.0,
            },
            {
                'nombre': 'PayPal',
                'tipo': 'paypal',
                'descripcion': 'Pago seguro a través de PayPal.',
                'comision': 2.5,
            },
            {
                'nombre': 'Contra Reembolso',
                'tipo': 'efectivo',
                'descripcion': 'Paga cuando recibas tu pedido.',
                'comision': 5.0,
            },
        ]
        
        # Contador para éxitos y existentes
        created = 0
        existing = 0
        
        for metodo in metodos:
            # Verificar si ya existe
            if not MetodoPago.objects.filter(tipo=metodo['tipo']).exists():
                # Crear el método de pago
                MetodoPago.objects.create(**metodo)
                self.stdout.write(self.style.SUCCESS(f'Creado método de pago: {metodo["nombre"]}'))
                created += 1
            else:
                self.stdout.write(self.style.WARNING(f'Ya existe método de pago: {metodo["nombre"]}'))
                existing += 1
        
        # Mensaje final
        if created:
            self.stdout.write(self.style.SUCCESS(f'Se crearon {created} métodos de pago.'))
        if existing:
            self.stdout.write(self.style.WARNING(f'Se omitieron {existing} métodos de pago existentes.'))
        if not created and not existing:
            self.stdout.write(self.style.ERROR('No se crearon métodos de pago.'))