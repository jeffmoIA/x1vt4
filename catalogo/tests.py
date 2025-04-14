from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalogo.models import Categoria, Marca, Producto, TallaProducto, ImagenProducto

class CategoriaModelTest(TestCase):
    """
    Tests para el modelo Categoria
    """
    def setUp(self):
        # Este método se ejecuta antes de cada test
        # Creamos una categoría para usar en los tests
        self.categoria = Categoria.objects.create(
            nombre="Cascos",
            descripcion="Protección para la cabeza"
        )
    
    def test_creacion_categoria(self):
        # Test para verificar que la categoría se crea correctamente
        self.assertTrue(isinstance(self.categoria, Categoria))
        self.assertEqual(self.categoria.__str__(), "Cascos")
    
    def test_verbose_name_plural(self):
        # Test para verificar que el verbose_name_plural es correcto
        self.assertEqual(str(Categoria._meta.verbose_name_plural), "Categorías")

class MarcaModelTest(TestCase):
    """
    Tests para el modelo Marca
    """
    def setUp(self):
        # Crear una marca para los tests
        self.marca = Marca.objects.create(
            nombre="Honda",
            descripcion="Fabricante japonés de motocicletas"
        )
    
    def test_creacion_marca(self):
        # Verificar que la marca se crea correctamente
        self.assertEqual(self.marca.nombre, "Honda")
        self.assertEqual(self.marca.__str__(), "Honda")

class ProductoModelTest(TestCase):
    """
    Tests para el modelo Producto
    """
    def setUp(self):
        # Crear objetos necesarios para los tests
        self.categoria = Categoria.objects.create(nombre="Motocicletas")
        self.marca = Marca.objects.create(nombre="Yamaha")
        
        # Crear un producto para los tests
        self.producto = Producto.objects.create(
            nombre="MT-07",
            descripcion="Motocicleta naked de media cilindrada",
            precio=8999.99,
            categoria=self.categoria,
            marca=self.marca,
            stock=10,
            disponible=True
        )
    
    def test_creacion_producto(self):
        # Verificar que el producto se crea correctamente
        self.assertEqual(self.producto.nombre, "MT-07")
        self.assertEqual(self.producto.precio, 8999.99)
        self.assertEqual(self.producto.categoria, self.categoria)
        self.assertEqual(self.producto.marca, self.marca)
        self.assertEqual(self.producto.__str__(), "MT-07")
    
    def test_get_imagen_url(self):
        # Test para el método get_imagen_url cuando no hay imagen
        self.assertTrue("placeholder" in self.producto.get_imagen_url())

class CatalogoViewsTest(TestCase):
    """
    Tests para las vistas de la aplicación catalogo
    """
    def setUp(self):
        # Crear un cliente para hacer peticiones HTTP
        self.client = self.client_class()
        
        # Crear un usuario para los tests
        self.usuario = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        
        # Crear objetos necesarios para los tests
        self.categoria = Categoria.objects.create(nombre="Motos")
        self.marca = Marca.objects.create(nombre="Ducati")
        
        # Crear varios productos para los tests
        for i in range(3):
            Producto.objects.create(
                nombre=f"Producto {i}",
                descripcion=f"Descripción del producto {i}",
                precio=100 + i * 10,
                categoria=self.categoria,
                marca=self.marca,
                stock=5,
                disponible=True
            )
    
    def test_lista_productos_view(self):
        # Test para la vista de lista de productos
        url = reverse('catalogo:lista_productos')
        response = self.client.get(url)
        
        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la plantilla correcta está siendo usada
        self.assertTemplateUsed(response, 'catalogo/lista_productos.html')
        
        # Verificar que los productos están en el contexto
        self.assertTrue('productos' in response.context)
    
    def test_detalle_producto_view(self):
        # Test para la vista de detalle de producto
        producto = Producto.objects.first()  # Obtener el primer producto
        url = reverse('catalogo:detalle_producto', args=[producto.id])
        response = self.client.get(url)
        
        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la plantilla correcta está siendo usada
        self.assertTemplateUsed(response, 'catalogo/detalle_producto.html')
        
        # Verificar que el producto está en el contexto
        self.assertEqual(response.context['producto'], producto)

class CatalogoViewsTestAvanzado(TestCase):
    """Tests adicionales para las vistas del catálogo"""
    
    def setUp(self):
        # Crear usuario para pruebas
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Crear categoría y marca
        self.categoria = Categoria.objects.create(nombre='Cascos')
        self.marca = Marca.objects.create(nombre='Test Brand')
        
        # Crear varios productos
        for i in range(5):
            Producto.objects.create(
                nombre=f'Producto {i}',
                descripcion=f'Descripción {i}',
                precio=50 + i * 10,
                categoria=self.categoria,
                marca=self.marca,
                stock=10,
                disponible=True
            )
        
        # Autenticar usuario
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_productos_por_categoria(self):
        """Test para ver productos por categoría"""
        url = reverse('catalogo:productos_por_categoria', args=[self.categoria.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_productos.html')
        self.assertEqual(response.context['categoria'], self.categoria)
    
    def test_productos_por_marca(self):
        """Test para ver productos por marca"""
        url = reverse('catalogo:productos_por_marca', args=[self.marca.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_productos.html')
        self.assertEqual(response.context['marca'], self.marca)
    
    def test_lista_productos_con_filtros(self):
        """Test para filtrar productos"""
        # Probar diferentes filtros
        filtros = {
            'nombre': 'Producto',
            'precio_min': '60',
            'precio_max': '80',
            'categoria': str(self.categoria.id),
            'marca': str(self.marca.id),
            'disponible': 'true'
        }
        
        url = reverse('catalogo:lista_productos')
        response = self.client.get(url, filtros)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_productos.html')