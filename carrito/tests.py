from django.test import TestCase, Client
from django.contrib.auth.models import User
from catalogo.models import Categoria, Marca, Producto
from carrito.models import Carrito, ItemCarrito
from decimal import Decimal
from django.urls import reverse

class CarritoModelTest(TestCase):
    """
    Tests para el modelo Carrito
    """
    def setUp(self):
        # Crear usuario, categoría, marca y producto para los tests
        self.usuario = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        
        self.categoria = Categoria.objects.create(nombre="Accesorios")
        self.marca = Marca.objects.create(nombre="Alpinestars")
        
        self.producto = Producto.objects.create(
            nombre="Guantes",
            descripcion="Guantes para motocicleta",
            precio=49.99,
            categoria=self.categoria,
            marca=self.marca,
            stock=20,
            disponible=True
        )
        
        # Crear un carrito para los tests
        self.carrito = Carrito.objects.create(usuario=self.usuario)
        
        # Añadir un item al carrito
        self.item = ItemCarrito.objects.create(
            carrito=self.carrito,
            producto=self.producto,
            cantidad=2
        )
    
    def test_carrito_str(self):
        # Test para el método __str__ del carrito
        self.assertEqual(str(self.carrito), f"Carrito de {self.usuario.username}")
    
    def test_carrito_total(self):
        # Test para el método total del carrito
        # El total debe ser precio * cantidad = 49.99 * 2 = 99.98
        self.assertEqual(self.carrito.total(), Decimal('99.98'))
    
    def test_item_carrito_str(self):
        # Test para el método __str__ del item del carrito
        self.assertEqual(str(self.item), f"2 x {self.producto.nombre}")
    
    def test_item_carrito_subtotal(self):
        # Test para el método subtotal del item del carrito
        # El subtotal debe ser precio * cantidad = 49.99 * 2 = 99.98
        from decimal import Decimal  # Importar Decimal aquí
        self.assertEqual(self.item.subtotal(), Decimal('99.98'))
        
class CarritoViewsTest(TestCase):
    """Tests para las vistas del carrito"""
    
    def setUp(self):
        # Crear usuario para pruebas
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Crear datos de prueba
        self.categoria = Categoria.objects.create(nombre='Cascos')
        self.marca = Marca.objects.create(nombre='Test Brand')
        
        # Crear producto de prueba
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            descripcion='Descripción de prueba',
            precio=50.00,
            categoria=self.categoria,
            marca=self.marca,
            stock=10,
            disponible=True
        )
        
        # Crear cliente y autenticar usuario
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # URLs para las pruebas
        self.url_ver_carrito = reverse('carrito:ver_carrito')
        self.url_agregar = reverse('carrito:agregar_al_carrito', args=[self.producto.id])
    
    def test_ver_carrito(self):
        """Test para la vista de ver carrito"""
        # Hacer solicitud GET
        response = self.client.get(self.url_ver_carrito)
        
        # Verificar que la respuesta es correcta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'carrito/carrito.html')
        self.assertIn('carrito', response.context)
    
    def test_agregar_al_carrito_post(self):
        """Test para agregar productos al carrito con POST"""
        # Datos para la solicitud POST
        data = {
            'cantidad': 2,
            'talla': 'M',
            'color': 'Negro'
        }
        
        # Hacer solicitud POST
        response = self.client.post(self.url_agregar, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el producto se agregó al carrito
        carrito = Carrito.objects.get(usuario=self.user)
        self.assertEqual(carrito.items.count(), 1)
        
        # Verificar detalles del item
        item = carrito.items.first()
        self.assertEqual(item.producto, self.producto)
        self.assertEqual(item.cantidad, 2)
        self.assertEqual(item.talla, 'M')
        self.assertEqual(item.color, 'Negro')
    
    def test_agregar_al_carrito_get(self):
        """Test para agregar productos al carrito con GET"""
        # Hacer solicitud GET
        response = self.client.get(self.url_agregar)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el producto se agregó al carrito
        carrito = Carrito.objects.get(usuario=self.user)
        self.assertEqual(carrito.items.count(), 1)
    
    def test_actualizar_carrito(self):
        """Test para actualizar la cantidad de un item en el carrito"""
        # Primero agregar un item al carrito
        carrito = Carrito.objects.create(usuario=self.user)
        item = ItemCarrito.objects.create(
            carrito=carrito,
            producto=self.producto,
            cantidad=1
        )
        
        # URL para actualizar
        url_actualizar = reverse('carrito:actualizar_carrito', args=[item.id])
        
        # Datos para la actualización
        data = {'cantidad': 3}
        
        # Hacer solicitud POST
        response = self.client.post(url_actualizar, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la cantidad se actualizó
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 3)
    
    def test_eliminar_del_carrito(self):
        """Test para eliminar un item del carrito"""
        # Primero agregar un item al carrito
        carrito = Carrito.objects.create(usuario=self.user)
        item = ItemCarrito.objects.create(
            carrito=carrito,
            producto=self.producto,
            cantidad=1
        )
        
        # URL para eliminar
        url_eliminar = reverse('carrito:eliminar_del_carrito', args=[item.id])
        
        # Hacer solicitud GET
        response = self.client.get(url_eliminar)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el item se eliminó
        self.assertEqual(carrito.items.count(), 0)