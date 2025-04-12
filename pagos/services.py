"""
Servicio de procesamiento de pagos que simula la integración con pasarelas de pago
y cumple con buenas prácticas de seguridad PCI DSS.
"""
import logging
import uuid
import time
import random
import hashlib
from decimal import Decimal
from django.conf import settings
from .models import Pago, HistorialPago
from django.utils import timezone

logger = logging.getLogger('mototienda.security')

class PaymentProcessor:
    """
    Procesador de pagos que encapsula la lógica de integración con diferentes
    pasarelas de pago y asegura que los datos sensibles se manejen correctamente.
    """
    
    @staticmethod
    def get_processor(method_type):
        """
        Factory method para obtener el procesador adecuado según el método de pago.
        
        Args:
            method_type (str): Tipo de método de pago (tarjeta, transferencia, etc.)
            
        Returns:
            Instancia del procesador adecuado
        """
        if method_type == 'tarjeta':
            return CardPaymentProcessor()
        elif method_type == 'transferencia':
            return BankTransferProcessor()
        elif method_type == 'paypal':
            return PayPalProcessor()
        elif method_type == 'efectivo':
            return CashOnDeliveryProcessor()
        else:
            raise ValueError(f"Método de pago no soportado: {method_type}")
    
    def process_payment(self, payment_data):
        """
        Método que debe ser implementado por clases concretas.
        """
        raise NotImplementedError("Las subclases deben implementar este método.")
    
    def validate_payment_data(self, payment_data):
        """
        Valida los datos de pago comunes a todos los métodos.
        
        Args:
            payment_data (dict): Datos del pago a validar
            
        Returns:
            tuple: (bool, str) - (éxito, mensaje de error si hay)
        """
        required_fields = ['monto', 'pedido', 'usuario']
        
        # Verificar campos requeridos
        for field in required_fields:
            if field not in payment_data:
                return False, f"Falta el campo requerido: {field}"
                
        # Validar monto
        try:
            amount = Decimal(payment_data['monto'])
            if amount <= 0:
                return False, "El monto debe ser mayor que cero"
        except (ValueError, TypeError):
            return False, "El monto debe ser un número válido"
            
        return True, ""
    
    def _sanitize_log_data(self, data):
        """
        Sanitiza los datos para el log (elimina información sensible).
        
        Args:
            data (dict): Datos a sanitizar
            
        Returns:
            dict: Datos seguros para el log
        """
        safe_data = data.copy()
        
        # Eliminar datos sensibles
        if 'card_number' in safe_data:
            safe_data['card_number'] = f"****{safe_data['card_number'][-4:]}" if len(safe_data['card_number']) >= 4 else "****"
        
        if 'cvv' in safe_data:
            safe_data['cvv'] = "***"
            
        if 'password' in safe_data:
            safe_data['password'] = "********"
            
        return safe_data
        
    def _log_payment_attempt(self, payment_data, success, message=""):
        """
        Registra un intento de pago en el log de seguridad.
        
        Args:
            payment_data (dict): Datos del pago
            success (bool): Éxito de la operación
            message (str): Mensaje adicional
        """
        # Sanitizar datos para log
        safe_data = self._sanitize_log_data(payment_data)
        
        # Crear mensaje de log
        log_message = f"Intento de pago: {success}, Monto: {safe_data.get('monto', 'N/A')}"
        if 'pedido' in safe_data and hasattr(safe_data['pedido'], 'id'):
            log_message += f", Pedido: {safe_data['pedido'].id}"
        if 'usuario' in safe_data and hasattr(safe_data['usuario'], 'username'):
            log_message += f", Usuario: {safe_data['usuario'].username}"
        if message:
            log_message += f", Mensaje: {message}"
        
        # Registrar en el log
        if success:
            logger.info(log_message)
        else:
            logger.warning(log_message)

class CardPaymentProcessor(PaymentProcessor):
    """
    Procesador para pagos con tarjeta que simula una integración con un gateway de pago
    y cumple con las directrices de PCI DSS.
    """
    
    def process_payment(self, payment_data):
        """
        Procesa un pago con tarjeta.
        
        Args:
            payment_data (dict): Datos del pago incluyendo:
                - monto: cantidad a pagar
                - pedido: objeto Pedido
                - usuario: objeto User
                - card_number: número de tarjeta (simulado)
                - card_expiry: fecha de expiración
                - cvv: código de seguridad
                
        Returns:
            tuple: (bool, str, str) - (éxito, mensaje, ID de transacción)
        """
        # Validar datos básicos
        valid, error_msg = self.validate_payment_data(payment_data)
        if not valid:
            self._log_payment_attempt(payment_data, False, error_msg)
            return False, error_msg, None
            
        # Validar datos específicos de tarjeta
        if not self._validate_card_data(payment_data):
            msg = "Datos de tarjeta inválidos"
            self._log_payment_attempt(payment_data, False, msg)
            return False, msg, None
            
        # En un sistema real, aquí se integraría con el procesador de pagos
        # Para el simulador, introducimos un retraso aleatorio y posibilidad de fallo
        time.sleep(random.uniform(1, 2))  # Simular latencia de API
        
        # Simular respuesta del procesador (aleatoria para demo)
        success_rate = 0.9  # 90% de probabilidad de éxito
        success = random.random() < success_rate
        
        # Generar ID de transacción única
        transaction_id = f"card_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        if success:
            msg = "Pago procesado correctamente"
            self._log_payment_attempt(payment_data, True, msg)
            return True, msg, transaction_id
        else:
            # Simulación de errores típicos
            errors = [
                "Fondos insuficientes",
                "Tarjeta rechazada por el banco",
                "Tarjeta expirada",
                "Error de comunicación con el banco"
            ]
            error_msg = random.choice(errors)
            self._log_payment_attempt(payment_data, False, error_msg)
            return False, error_msg, None
    
    def _validate_card_data(self, payment_data):
        """
        Valida que todos los datos necesarios de la tarjeta estén presentes.
        
        Args:
            payment_data (dict): Datos del pago con información de tarjeta
            
        Returns:
            bool: True si los datos son válidos
        """
        required_card_fields = ['card_number', 'card_expiry', 'cvv']
        
        # Verificar campos requeridos
        for field in required_card_fields:
            if field not in payment_data:
                return False
                
        # Validaciones básicas
        # Número de tarjeta: entre 13-19 dígitos
        card_number = payment_data['card_number'].replace(' ', '')
        if not card_number.isdigit() or not (13 <= len(card_number) <= 19):
            return False
            
        # Validar fecha de expiración (formato: MM/YY)
        expiry = payment_data['card_expiry']
        if not isinstance(expiry, str) or len(expiry) != 5 or expiry[2] != '/':
            return False
            
        try:
            month, year = expiry.split('/')
            month = int(month)
            year = int(f"20{year}")  # Asumiendo formato YY para el año
            
            # Verificar que la fecha sea válida y en el futuro
            now = timezone.now()
            if not (1 <= month <= 12) or year < now.year or (year == now.year and month < now.month):
                return False
        except (ValueError, IndexError):
            return False
            
        # Validar CVV: 3-4 dígitos
        cvv = payment_data['cvv']
        if not isinstance(cvv, str) or not cvv.isdigit() or not (3 <= len(cvv) <= 4):
            return False
            
        return True

class BankTransferProcessor(PaymentProcessor):
    """Procesador para pagos por transferencia bancaria."""
    
    def process_payment(self, payment_data):
        """
        Registra una transferencia bancaria pendiente.
        
        Args:
            payment_data (dict): Datos del pago incluyendo:
                - monto: cantidad a pagar
                - pedido: objeto Pedido
                - usuario: objeto User
                
        Returns:
            tuple: (bool, str, str) - (éxito, mensaje, ID de transacción)
        """
        # Validar datos básicos
        valid, error_msg = self.validate_payment_data(payment_data)
        if not valid:
            self._log_payment_attempt(payment_data, False, error_msg)
            return False, error_msg, None
            
        # Generar referencia única para la transferencia
        reference = f"TRF{int(time.time())}_{uuid.uuid4().hex[:6].upper()}"
        
        # En un sistema real, se enviarían instrucciones por email, etc.
        
        msg = f"Transferencia bancaria registrada. Referencia: {reference}"
        self._log_payment_attempt(payment_data, True, msg)
        return True, msg, reference

class PayPalProcessor(PaymentProcessor):
    """Procesador para pagos vía PayPal."""
    
    def process_payment(self, payment_data):
        """
        Simula un pago a través de PayPal.
        
        Args:
            payment_data (dict): Datos del pago incluyendo:
                - monto: cantidad a pagar
                - pedido: objeto Pedido
                - usuario: objeto User
                - paypal_email: email de PayPal (opcional)
                
        Returns:
            tuple: (bool, str, str) - (éxito, mensaje, ID de transacción)
        """
        # Validar datos básicos
        valid, error_msg = self.validate_payment_data(payment_data)
        if not valid:
            self._log_payment_attempt(payment_data, False, error_msg)
            return False, error_msg, None
            
        # Simular una redirección a PayPal y respuesta
        time.sleep(random.uniform(1, 2))  # Simular latencia
        
        # Simulación de respuesta
        success_rate = 0.95  # 95% de probabilidad de éxito
        success = random.random() < success_rate
        
        # Generar ID de transacción PayPal
        paypal_id = f"PP-{int(time.time())}-{uuid.uuid4().hex[:10].upper()}"
        
        if success:
            msg = "Pago por PayPal completado correctamente"
            self._log_payment_attempt(payment_data, True, msg)
            return True, msg, paypal_id
        else:
            error_msg = "Error en el proceso de pago con PayPal"
            self._log_payment_attempt(payment_data, False, error_msg)
            return False, error_msg, None

class CashOnDeliveryProcessor(PaymentProcessor):
    """Procesador para pagos contra entrega."""
    
    def process_payment(self, payment_data):
        """
        Registra un pago contra entrega.
        
        Args:
            payment_data (dict): Datos del pago incluyendo:
                - monto: cantidad a pagar
                - pedido: objeto Pedido
                - usuario: objeto User
                
        Returns:
            tuple: (bool, str, str) - (éxito, mensaje, ID de transacción)
        """
        # Validar datos básicos
        valid, error_msg = self.validate_payment_data(payment_data)
        if not valid:
            self._log_payment_attempt(payment_data, False, error_msg)
            return False, error_msg, None
            
        # Generar referencia para el pago contra entrega
        reference = f"COD{int(time.time())}_{uuid.uuid4().hex[:6].upper()}"
        
        msg = "Pago contra entrega registrado correctamente"
        self._log_payment_attempt(payment_data, True, msg)
        return True, msg, reference