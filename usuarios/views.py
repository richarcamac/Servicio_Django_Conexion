# python
# File: `usuarios/views.py`
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .forms import RegistroForm, LoginForm
from .models import Usuario
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.mail import send_mail, get_connection
from django.utils.crypto import get_random_string
from django.conf import settings
from datetime import timedelta
from django.db import IntegrityError
import traceback

# Intentar importar la SDK oficial de SendGrid
try:
    from sendgrid import SendGridAPIClient
except Exception:
    SendGridAPIClient = None

@csrf_exempt
def registro_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    # Obtener datos según content-type
    content_type = request.META.get('CONTENT_TYPE', '')
    if 'application/json' in content_type:
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
        form = RegistroForm(data)
    else:
        form = RegistroForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'success': False, 'error': 'Datos inválidos', 'details': form.errors}, status=400)

    try:
        usuario = form.save()
        return JsonResponse({'success': True, 'message': 'Usuario registrado correctamente.'}, status=201)
    except IntegrityError as e:
        # Manejar duplicado en correo u otros unique constraints
        if 'correo' in str(e).lower() or 'unique' in str(e).lower():
            return JsonResponse({'success': False, 'error': 'El correo electrónico ya está registrado.'}, status=409)
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'No se pudo registrar el usuario.'}, status=500)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'No se pudo registrar el usuario.'}, status=500)

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    content_type = request.META.get('CONTENT_TYPE', '')
    if 'application/json' in content_type:
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
        form = LoginForm(data)
    else:
        form = LoginForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'success': False, 'error': 'Datos inválidos', 'details': form.errors}, status=400)

    try:
        correo = form.cleaned_data['correo']
        password = form.cleaned_data['password']
        usuario = authenticate(request, correo=correo, password=password)
        if usuario is not None:
            login(request, usuario)
            usuario.fechaultimoingreso = timezone.now()
            usuario.save()
            return JsonResponse({'success': True, 'message': 'Login exitoso.'}, status=200)
        else:
            return JsonResponse({'success': False, 'error': 'Correo o contraseña incorrectos.'}, status=401)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Error en login'}, status=500)

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'usuarios/home.html')

@csrf_exempt
def recuperar_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    # parseo seguro
    content_type = request.META.get('CONTENT_TYPE', '')
    if 'application/json' in content_type:
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    else:
        data = request.POST

    correo = data.get('correo')
    if not correo:
        return JsonResponse({'success': False, 'error': 'Correo requerido'}, status=400)

    try:
        usuario = Usuario.objects.get(correo=correo)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Correo no registrado'}, status=404)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Error al buscar usuario'}, status=500)

    codigo = get_random_string(length=6)
    usuario.codigo_recuperacion = codigo
    usuario.codigo_expiracion = timezone.now() + timedelta(minutes=10)
    usuario.save()

    backend_used = None
    sendgrid_result = None

    # Intentar SendGrid SDK si está disponible y hay API key
    try:
        from sendgrid import SendGridAPIClient
        sg_ok = True
    except Exception:
        SendGridAPIClient = None
        sg_ok = False

    if sg_ok and settings.SENDGRID_API_KEY:
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            request_body = {
                "personalizations": [{"to": [{"email": correo}], "subject": "Recuperación de contraseña"}],
                "from": {"email": settings.DEFAULT_FROM_EMAIL},
                "content": [{"type": "text/plain", "value": f"Tu código de recuperación es: {codigo}"}],
            }
            resp = sg.client.mail.send.post(request_body=request_body)
            # resp puede ser un objeto con status_code / body o similar según la versión
            status_code = getattr(resp, "status_code", None)
            body = getattr(resp, "body", None)
            sendgrid_result = {"status_code": status_code, "body": str(body)[:1000]}
            backend_used = "sendgrid_sdk"
            if status_code and int(status_code) in (200, 202):
                return JsonResponse({'success': True, 'message': 'Código enviado al correo.', 'backend': backend_used, 'sendgrid': sendgrid_result}, status=200)
            # si status_code indica error, continuamos al fallback y lo reportamos
        except Exception as e:
            traceback.print_exc()
            sendgrid_result = {"error": str(e)}
            backend_used = "sendgrid_sdk_error"

    # Fallback: usar django.core.mail (usa settings.EMAIL_BACKEND; si apunta a un backend inexistente, usar console)
    try:
        try:
            conn = get_connection()  # intenta usar settings.EMAIL_BACKEND
            backend_used = backend_used or 'configured_email_backend'
        except ModuleNotFoundError:
            # backend configurado no existe (p.ej. sendgrid_django no instalado)
            conn = get_connection(backend='django.core.mail.backends.console.EmailBackend')
            backend_used = backend_used or 'console_fallback'

        send_mail(
            'Recuperación de contraseña',
            f'Tu código de recuperación es: {codigo}',
            settings.DEFAULT_FROM_EMAIL,
            [correo],
            fail_silently=False,
            connection=conn,
        )
        return JsonResponse({'success': True, 'message': 'Código enviado al correo.', 'backend': backend_used, 'sendgrid': sendgrid_result}, status=200)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Error al enviar código', 'detail': str(e), 'backend': backend_used, 'sendgrid': sendgrid_result}, status=500)
