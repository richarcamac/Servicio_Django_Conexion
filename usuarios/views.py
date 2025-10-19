# python
# File: `usuarios/views.py`
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from .forms import RegistroForm, LoginForm
from .models import Usuario, Producto
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.mail import send_mail, get_connection
from django.utils.crypto import get_random_string
from django.conf import settings
from datetime import datetime, timedelta
from django.db import IntegrityError
import traceback

@csrf_exempt
def registro_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
            form = RegistroForm(data)
        else:
            form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                return JsonResponse({'success': True, 'message': 'Usuario registrado correctamente.'}, status=201)
            except Exception as e:
                # Controlar error de correo duplicado
                if 'Duplicate entry' in str(e) and 'correo' in str(e):
                    return JsonResponse({'success': False, 'error': 'El correo electrónico ya está registrado.'}, status=409)
                return JsonResponse({'success': False, 'error': 'No se pudo registrar el usuario.'}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Datos inválidos', 'details': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
            form = LoginForm(data)
        else:
            form = LoginForm(request.POST)
        if form.is_valid():
            try:
                correo = form.cleaned_data['correo']
                password = form.cleaned_data['password']
                usuario = authenticate(request, correo=correo, password=password)
                if usuario is not None:
                    login(request, usuario)
                    usuario.fechaultimoingreso = timezone.now()
                    usuario.save()
                    # Devolver también rol y datos mínimos para la app cliente
                    return JsonResponse({'success': True, 'message': 'Login exitoso.', 'rol': usuario.rol, 'nombre': usuario.nombre, 'id': usuario.id}, status=200)
                else:
                    return JsonResponse({'success': False, 'error': 'Correo o contraseña incorrectos.'}, status=401)
            except Exception as e:
                traceback.print_exc()
                return JsonResponse({'success': False, 'error': 'Error en login'}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Datos inválidos', 'details': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def logout_view(request):
    logout(request)
    return redirect('login')

# Home view: intentar renderizar plantilla, si falla devolver respuesta simple para diagnóstico
def home_view(request):
    try:
        return render(request, 'usuarios/home.html')
    except TemplateDoesNotExist:
        return HttpResponse('<h1>Asiri - Home</h1><p>Plantilla usuarios/home.html no encontrada. Esto es una respuesta de respaldo.</p>')

@csrf_exempt
def recuperar_view(request):
    """Envia código de recuperación por correo. (ya existente)
    Espera JSON { "correo": "..." }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            correo = data.get('correo')
            if not correo:
                return JsonResponse({'success': False, 'error': 'Correo requerido'}, status=400)
            try:
                usuario = Usuario.objects.get(correo=correo)
            except Usuario.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Correo no registrado'}, status=404)
            codigo = get_random_string(length=6)
            usuario.codigo_recuperacion = codigo
            usuario.codigo_expiracion = timezone.now() + timedelta(minutes=10)
            usuario.save()
            # Enviar con SendGrid API si está configurada, si no, usar get_connection/console
            api_key = getattr(settings, 'SENDGRID_API_KEY', '') or None
            send_result = None
            if api_key:
                try:
                    url = "https://api.sendgrid.com/v3/mail/send"
                    payload = {
                        "personalizations": [
                            {"to": [{"email": correo}], "subject": "Recuperación de contraseña"}
                        ],
                        "from": {"email": settings.DEFAULT_FROM_EMAIL},
                        "content": [
                            {"type": "text/plain", "value": f"Tu código de recuperación es: {codigo}"}
                        ]
                    }
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    resp = requests.post(url, json=payload, headers=headers, timeout=10)
                    send_result = {"status_code": resp.status_code, "body": resp.text[:1000]}
                    if resp.status_code in (200, 202):
                        return JsonResponse({'success': True, 'message': 'Código enviado al correo.', 'backend': 'sendgrid_api', 'sendgrid': send_result}, status=200)
                except Exception as e:
                    traceback.print_exc()
                    send_result = {"error": str(e)}
            # fallback
            try:
                conn = get_connection()
            except Exception:
                conn = get_connection(backend='django.core.mail.backends.console.EmailBackend')
            try:
                send_mail('Recuperación de contraseña', f'Tu código de recuperación es: {codigo}', settings.DEFAULT_FROM_EMAIL, [correo], fail_silently=False, connection=conn)
            except Exception as e:
                traceback.print_exc()
                return JsonResponse({'success': False, 'error': 'Error al enviar código', 'detail': str(e)}, status=500)
            return JsonResponse({'success': True, 'message': 'Código enviado al correo.', 'backend': 'console_fallback', 'sendgrid': send_result}, status=200)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': 'Error al procesar la solicitud', 'detail': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def verificar_codigo_view(request):
    """Verifica que el código enviado por correo es válido y no expiró.
    Espera JSON: { "correo": "...", "codigo": "..." }
    Responde { success: true } o { success: false, error: ... }
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    correo = data.get('correo')
    codigo = data.get('codigo')
    if not correo or not codigo:
        return JsonResponse({'success': False, 'error': 'Correo y código son requeridos'}, status=400)
    try:
        usuario = Usuario.objects.get(correo=correo)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Correo no registrado'}, status=404)
    if not usuario.codigo_recuperacion or usuario.codigo_recuperacion != codigo:
        return JsonResponse({'success': False, 'error': 'Código inválido'}, status=401)
    if not usuario.codigo_expiracion or timezone.now() > usuario.codigo_expiracion:
        return JsonResponse({'success': False, 'error': 'Código expirado'}, status=410)
    return JsonResponse({'success': True, 'message': 'Código válido'}, status=200)

@csrf_exempt
def resetear_password_view(request):
    """Resetea la contraseña usando correo + código + nueva_password
    Espera JSON: { "correo": "...", "codigo": "...", "password": "..." }
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    correo = data.get('correo')
    codigo = data.get('codigo')
    new_password = data.get('password')
    if not correo or not codigo or not new_password:
        return JsonResponse({'success': False, 'error': 'Correo, código y nueva contraseña son requeridos'}, status=400)
    if len(new_password) < 6:
        return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}, status=400)
    try:
        usuario = Usuario.objects.get(correo=correo)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Correo no registrado'}, status=404)
    if not usuario.codigo_recuperacion or usuario.codigo_recuperacion != codigo:
        return JsonResponse({'success': False, 'error': 'Código inválido'}, status=401)
    if not usuario.codigo_expiracion or timezone.now() > usuario.codigo_expiracion:
        return JsonResponse({'success': False, 'error': 'Código expirado'}, status=410)
    try:
        usuario.set_password(new_password)
        # limpiar código para que no pueda reutilizarse
        usuario.codigo_recuperacion = None
        usuario.codigo_expiracion = None
        usuario.save()
        return JsonResponse({'success': True, 'message': 'Contraseña actualizada correctamente.'}, status=200)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Error al actualizar la contraseña'}, status=500)

@csrf_exempt
def productos_list(request):
    """Devuelve lista de productos en JSON. También acepta GET para la UI de Kotlin."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    productos = Producto.objects.filter(estado=True)
    data = []
    for p in productos:
        data.append({
            'id': p.id,
            'titulo': p.titulo,
            'descripcion': p.descripcion,
            'imagen': p.imagen,
            'unidad': p.unidad,
            'precio': str(p.precio),
            'moneda': p.moneda,
            'cantidad': p.cantidad,
            'fecharegistro': p.fecharegistro.isoformat(),
        })
    return JsonResponse({'success': True, 'productos': data}, status=200)

@csrf_exempt
def producto_detail(request, id):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    try:
        p = Producto.objects.get(id=id)
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
    data = {
        'id': p.id,
        'titulo': p.titulo,
        'descripcion': p.descripcion,
        'imagen': p.imagen,
        'unidad': p.unidad,
        'precio': str(p.precio),
        'moneda': p.moneda,
        'cantidad': p.cantidad,
        'fecharegistro': p.fecharegistro.isoformat(),
    }
    return JsonResponse({'success': True, 'producto': data}, status=200)

@csrf_exempt
def productos_sample(request):
    """Crear productos de ejemplo si la tabla está vacía (uso de prueba)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    try:
        if Producto.objects.count() == 0:
            ejemplos = [
                {
                    'titulo': 'Manzana Roja',
                    'descripcion': 'Manzana fresca y jugosa, origen local.',
                    'imagen': 'https://via.placeholder.com/200?text=Manzana',
                    'unidad': 'kg',
                    'precio': '3.50',
                    'moneda': 'USD',
                    'cantidad': 100,
                },
                {
                    'titulo': 'Pan Artesanal',
                    'descripcion': 'Pan hecho a mano, ideal para desayuno.',
                    'imagen': 'https://via.placeholder.com/200?text=Pan',
                    'unidad': 'pieza',
                    'precio': '1.20',
                    'moneda': 'USD',
                    'cantidad': 50,
                },
                {
                    'titulo': 'Café Molido',
                    'descripcion': 'Café premium, tostado medio.',
                    'imagen': 'https://via.placeholder.com/200?text=Cafe',
                    'unidad': 'bag',
                    'precio': '8.75',
                    'moneda': 'USD',
                    'cantidad': 30,
                },
            ]
            for e in ejemplos:
                Producto.objects.create(
                    titulo=e['titulo'], descripcion=e['descripcion'], imagen=e['imagen'], unidad=e['unidad'], precio=e['precio'], moneda=e['moneda'], cantidad=e['cantidad']
                )
            return JsonResponse({'success': True, 'message': 'Productos de ejemplo creados.'}, status=201)
        else:
            return JsonResponse({'success': False, 'error': 'Ya existen productos.'}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Error al crear ejemplos', 'detail': str(e)}, status=500)
