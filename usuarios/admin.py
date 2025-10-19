from django.contrib import admin
from .models import Usuario, Producto

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'nombre', 'rol', 'is_active', 'fecharegistro')
    search_fields = ('correo', 'nombre')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'precio', 'moneda', 'estado', 'fecharegistro', 'cantidad')
    search_fields = ('titulo', 'descripcion')
    list_filter = ('estado', 'moneda')
