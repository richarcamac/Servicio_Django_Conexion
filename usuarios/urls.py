from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, RegistrarProductoAPIView, ListarProductosAPIView, RegistrarPedidoAPIView, ListarPedidosAPIView, CambiarEstadoPedidoAPIView, registrar_compra_view, listar_compras_view

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('recuperar/', views.recuperar_view, name='recuperar'),  # Enviar código
    path('recuperar/verify/', views.verificar_codigo_view, name='recuperar_verify'),  # Verificar código
    path('recuperar/reset/', views.resetear_password_view, name='recuperar_reset'),  # Resetear contraseña

    # Productos
    path('productos/', views.productos_list, name='productos_list'),
    path('productos/sample/', views.productos_sample, name='productos_sample'),
    # path('productos/<int:id>/', views.producto_detail, name='producto_detail'),
    path('api/registrar_producto/', RegistrarProductoAPIView.as_view(), name='registrar_producto'),
    path('api/listar_productos/', ListarProductosAPIView.as_view(), name='listar_productos'),
    path('api/registrar_pedido/', RegistrarPedidoAPIView.as_view(), name='registrar_pedido'),
    path('api/listar_pedidos/', ListarPedidosAPIView.as_view(), name='listar_pedidos'),
    path('api/cambiar_estado_pedido/<int:pk>/', CambiarEstadoPedidoAPIView.as_view(), name='cambiar_estado_pedido'),
    path('api/registrar_compra/', registrar_compra_view, name='registrar_compra'),
    path('api/listar_compras/', listar_compras_view, name='listar_compras'),
    path('api/', include(router.urls)),  # <-- Agrega el router bajo /api/
]









