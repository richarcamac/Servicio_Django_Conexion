from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, password=None, rol=None, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        usuario = self.model(correo=correo, nombre=nombre, rol=rol, **extra_fields)
        usuario.set_password(password)
        usuario.fecharegistro = timezone.now()
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo, nombre, password=None, **extra_fields):
        extra_fields.setdefault('rol', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(correo, nombre, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=50, unique=True)
    rol = models.CharField(max_length=20)
    status = models.BooleanField(default=True)
    fecharegistro = models.DateTimeField(default=timezone.now)
    fechaultimoingreso = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    codigo_recuperacion = models.CharField(max_length=10, null=True, blank=True)
    codigo_expiracion = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.correo

class Producto(models.Model):
    """Modelo para productos que usarán el front Kotlin y la API."""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    imagen = models.TextField(blank=True, null=True)  # Ahora almacena base64
    unidad = models.CharField(max_length=50, default='unidad')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10, default='COP')
    estado = models.BooleanField(default=True)
    fecharegistro = models.DateTimeField(default=timezone.now)
    cantidad = models.IntegerField(default=0)

    class Meta:
        ordering = ['-fecharegistro']

    def __str__(self):
        return self.titulo

class MaestroPedido(models.Model):
    fecha_registro = models.DateTimeField(auto_now_add=True)
    codigo_cliente = models.CharField(max_length=50)
    nombre_cliente = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    numero_celular = models.CharField(max_length=15)
    estado = models.CharField(max_length=20, default='Solicitud')  # Nuevo campo

class DetallePedido(models.Model):
    maestro = models.ForeignKey(MaestroPedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
