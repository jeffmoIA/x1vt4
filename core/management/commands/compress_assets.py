# Este comando comprime los assets (CSS, JS) para producción
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import subprocess
import time

class Command(BaseCommand):
    help = 'Comprime y optimiza todos los assets para producción'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Forzar la recompresión de todos los archivos',
        )
    
    def handle(self, *args, **options):
        """Comprime y optimiza assets para producción"""
        start_time = time.time()
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('Iniciando compresión de assets...'))
        
        # 1. Collect static files
        self.stdout.write('Colectando archivos estáticos...')
        call_command('collectstatic', interactive=False, verbosity=0)
        
        # 2. Compress using django-compressor
        self.stdout.write('Comprimiendo archivos CSS y JS...')
        if force:
            # Eliminar archivos comprimidos anteriores
            compressed_dir = os.path.join(settings.STATIC_ROOT, 'CACHE')
            if os.path.exists(compressed_dir):
                for root, dirs, files in os.walk(compressed_dir):
                    for file in files:
                        os.remove(os.path.join(root, file))
                self.stdout.write('Caché de compresión eliminada')
        
        # Comprimir
        call_command('compress', force=force, verbosity=2)
        
        # 3. Optimizar imágenes si el paquete pillow está instalado
        try:
            from PIL import Image
            self.stdout.write('Optimizando imágenes...')
            
            # Media dirs to optimize
            media_dirs = [
                os.path.join(settings.MEDIA_ROOT, 'productos'),
                os.path.join(settings.MEDIA_ROOT, 'marcas'),
            ]
            
            total_saved = 0
            images_processed = 0
            
            for media_dir in media_dirs:
                if not os.path.exists(media_dir):
                    continue
                    
                for root, dirs, files in os.walk(media_dir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            file_path = os.path.join(root, file)
                            try:
                                # Get original size
                                original_size = os.path.getsize(file_path)
                                
                                # Optimize image
                                with Image.open(file_path) as img:
                                    # Preserve EXIF data if present
                                    exif = img.info.get('exif')
                                    
                                    # Optimize quality
                                    img.save(file_path, optimize=True, quality=85, exif=exif if exif else "")
                                
                                # Get new size
                                new_size = os.path.getsize(file_path)
                                saved = original_size - new_size
                                total_saved += saved
                                images_processed += 1
                                
                                if saved > 0:
                                    self.stdout.write(f'  ✓ {file}: {saved/1024:.1f}KB ahorrados')
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f'  ✗ Error al optimizar {file}: {str(e)}'))
            
            if images_processed > 0:
                self.stdout.write(self.style.SUCCESS(
                    f'Optimizadas {images_processed} imágenes, ahorrando {total_saved/1024/1024:.2f}MB en total'
                ))
            else:
                self.stdout.write('No se encontraron imágenes para optimizar')
                
        except ImportError:
            self.stdout.write(self.style.WARNING('Pillow no está instalado, omitiendo optimización de imágenes'))
        
        # Mostrar tiempo total
        end_time = time.time()
        self.stdout.write(self.style.SUCCESS(
            f'Compresión completada en {end_time - start_time:.2f} segundos'
        ))