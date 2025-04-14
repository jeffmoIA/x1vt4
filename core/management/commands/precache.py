from django.core.management.base import BaseCommand
from django.core.cache import cache
from catalogo.models import Producto, Categoria, Marca
from django.db.models import Prefetch
import time
import logging

logger = logging.getLogger('mototienda.performance')

class Command(BaseCommand):
    help = 'Precarga las cachés más importantes para mejorar el rendimiento inicial'
    
    def handle(self, *args, **options):
        """Ejecuta la precarga de cachés"""
        start_time = time.time()
        self.stdout.write(self.style.SUCCESS('Iniciando precarga de cachés...'))
        
        # 1. Cachear categorías
        self.stdout.write('Cacheando categorías...')
        categorias = list(Categoria.objects.all())
        cache.set('todas_categorias', categorias, 3600 * 12)  # 12 horas
        
        # 2. Cachear marcas
        self.stdout.write('Cacheando marcas...')
        marcas = list(Marca.objects.all())
        cache.set('todas_marcas', marcas, 3600 * 12)  # 12 horas
        
        # 3. Cachear productos populares
        self.stdout.write('Cacheando productos populares...')
        productos_populares = list(Producto.objects
                                  .filter(disponible=True)
                                  .order_by('-stock')
                                  .select_related('categoria', 'marca')
                                  .prefetch_related('imagenes')[:12])
        cache.set('productos_populares', productos_populares, 3600 * 3)  # 3 horas
        
        # 4. Cachear productos por categoría
        self.stdout.write('Cacheando productos por categoría...')
        for categoria in categorias:
            productos = list(Producto.objects
                            .filter(categoria=categoria, disponible=True)
                            .select_related('marca')
                            .prefetch_related('imagenes')[:20])  # 20 productos por categoría
            cache_key = f'categoria_{categoria.id}_productos'
            cache.set(cache_key, productos, 3600 * 6)  # 6 horas
        
        # 5. Cachear productos por marca
        self.stdout.write('Cacheando productos por marca...')
        for marca in marcas:
            productos = list(Producto.objects
                            .filter(marca=marca, disponible=True)
                            .select_related('categoria')
                            .prefetch_related('imagenes')[:20])
            cache_key = f'marca_{marca.id}_productos'
            cache.set(cache_key, productos, 3600 * 6)  # 6 horas
        
        # Tiempo total
        end_time = time.time()
        total_time = end_time - start_time
        
        self.stdout.write(self.style.SUCCESS(
            f'Precarga de cachés completada en {total_time:.2f} segundos'
        ))
        
        # Mostrar estadísticas
        self.stdout.write(f"Categorías cacheadas: {len(categorias)}")
        self.stdout.write(f"Marcas cacheadas: {len(marcas)}")
        self.stdout.write(f"Total de cachés creadas: {len(categorias) + len(marcas) + 1 + len(categorias) + len(marcas)}")