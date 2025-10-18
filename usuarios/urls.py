from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('recuperar/', views.recuperar_view, name='recuperar'),  # Enviar código
    path('recuperar/verify/', views.verificar_codigo_view, name='recuperar_verify'),  # Verificar código
    path('recuperar/reset/', views.resetear_password_view, name='recuperar_reset'),  # Resetear contraseña
]



