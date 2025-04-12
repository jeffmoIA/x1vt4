from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    # Selección de método de pago
    path('seleccionar/<int:pedido_id>/', 
         views.seleccionar_metodo_pago, 
         name='seleccionar_metodo_pago'),
    
    # Procesamiento de pago
    path('procesar/<int:pago_id>/', 
         views.procesar_pago, 
         name='procesar_pago'),
    
    # Resumen de pago
    path('resumen/<int:pago_id>/', 
         views.resumen_pago, 
         name='resumen_pago'),
    
    # Redirección para PayPal
    path('paypal/<int:pago_id>/', 
         views.PayPalRedirectView.as_view(), 
         name='paypal_redirect'),
]