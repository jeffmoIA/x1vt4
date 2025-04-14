from django.test import TestCase, Client
from django.contrib.auth.models import User
from catalogo.models import Categoria, Marca, Producto
from pedidos.models import Pedido, ItemPedido, HistorialEstadoPedido
from decimal import Decimal
from django.urls import reverse

class PedidoModelTest(TestCase):
    """
    Tests para el modelo Pedido
    """
    def setUp(self):
        # Crear usuario para los tests
        self.usuario = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        
        # Crear categoría, marca y producto para los tests
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
        
        # Crear un pedido para los tests
        self.pedido = Pedido.objects.create(
            usuario=self.usuario,
            nombre_completo="Test User",
            direccion="Calle Principal 123",
            ciudad="Ciudad Test",
            codigo_postal="12345",
            telefono="123456789"
        )
        
        # Añadir un item al pedido
        self.item_pedido = ItemPedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            precio=49.99,
            cantidad=2
        )
    
    def test_pedido_str(self):
        # Test para el método __str__ del pedido
        self.assertEqual(str(self.pedido), f'Pedido {self.pedido.id} - {self.usuario.username}')
    
    def test_pedido_total(self):
        # Test para el método total del pedido
        # El total debe ser precio * cantidad = 49.99 * 2 = 99.98
        self.assertEqual(self.pedido.total(), Decimal('99.98'))
    
    def test_cambiar_estado(self):
        # Test para el método cambiar_estado del pedido
        # El estado inicial debe ser 'pendiente'
        self.assertEqual(self.pedido.estado, 'pendiente')
        
        # Cambiar el estado a 'procesando'
        resultado = self.pedido.cambiar_estado('procesando', "Cambiando estado para test")
        
        # Verificar que el cambio fue exitoso
        self.assertTrue(resultado)
        self.assertEqual(self.pedido.estado, 'procesando')
        
        # Verificar que se creó un registro en el historial
        historial = HistorialEstadoPedido.objects.filter(pedido=self.pedido)
        self.assertEqual(historial.count(), 1)
        
        # Verificar los datos del historial
        historial_item = historial.first()
        self.assertEqual(historial_item.estado_anterior, 'pendiente')
        self.assertEqual(historial_item.estado_nuevo, 'procesando')
        self.assertEqual(historial_item.notas, "Cambiando estado para test")

class PedidosViewsTest(TestCase):
    """Tests para las vistas de pedidos"""
    
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
        
        # Crear pedido de prueba
        self.pedido = Pedido.objects.create(
            usuario=self.user,
            nombre_completo='Test User',
            direccion='Test Address',
            ciudad='Test City',
            codigo_postal='12345',
            telefono='123456789'
        )
        
        # Añadir item al pedido
        ItemPedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            precio=50.00,
            cantidad=2
        )
        
        # Autenticar usuario
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_lista_pedidos(self):
        """Test para la vista de lista de pedidos"""
        url = reverse('pedidos:lista_pedidos')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/lista_pedidos.html')
        self.assertIn('pedidos', response.context)
    
    def test_detalle_pedido(self):
        """Test para la vista de detalle de pedido"""
        url = reverse('pedidos:detalle_pedido', args=[self.pedido.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/detalle_pedido.html')
        self.assertEqual(response.context['pedido'], self.pedido)
    
    def test_cancelar_pedido_get(self):
        """Test para la vista de cancelar pedido (GET)"""
        url = reverse('pedidos:cancelar_pedido', args=[self.pedido.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/confirmar_cancelacion.html')
    
    def test_cancelar_pedido_post(self):
        """Test para la vista de cancelar pedido (POST)"""
        url = reverse('pedidos:cancelar_pedido', args=[self.pedido.id])
        response = self.client.post(url)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el pedido se canceló
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'cancelado')

class PedidosUtilsTest(TestCase):
    """Tests para las utilidades de pedidos"""
    
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
        
        # Crear pedido de prueba
        self.pedido = Pedido.objects.create(
            usuario=self.user,
            nombre_completo='Test User',
            direccion='Test Address',
            ciudad='Test City',
            codigo_postal='12345',
            telefono='123456789'
        )
        
        # Añadir item al pedido
        ItemPedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            precio=50.00,
            cantidad=2
        )
    
    def test_generar_factura_pdf(self):
        """Test para generar factura PDF"""
        from pedidos.utils import generar_factura_pdf
        
        # Generar factura
        buffer = generar_factura_pdf(self.pedido)
        
        # Verificar que el buffer tiene contenido
        self.assertTrue(buffer.getvalue())
        self.assertGreater(len(buffer.getvalue()), 0)
    
    def test_obtener_factura(self):
        """Test para obtener factura"""
        from django.http import HttpRequest
        
        # Crear un request manual
        request = HttpRequest()
        request.user = self.user
        
        # Solicitar factura
        from pedidos.utils import obtener_factura
        response = obtener_factura(request, self.pedido.id)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')