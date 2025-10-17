from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from .forms import RegistroForm, LoginForm
from .models import Usuario
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from datetime import datetime, timedelta

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
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
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
                    return JsonResponse({'success': True, 'message': 'Login exitoso.'}, status=200)
                else:
                    return JsonResponse({'success': False, 'error': 'Correo o contraseña incorrectos.'}, status=401)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'Error en login'}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'usuarios/home.html')

@csrf_exempt
def recuperar_view(request):
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
            try:
                send_mail(
                    'Recuperación de contraseña',
                    f'Tu código de recuperación es: {codigo}',
                    settings.DEFAULT_FROM_EMAIL,
                    [correo],
                    fail_silently=False,
                )
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                return JsonResponse({'success': False, 'error': 'Error al enviar código', 'detail': str(e)}, status=500)
            return JsonResponse({'success': True, 'message': 'Código enviado al correo.'}, status=200)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': 'Error al procesar la solicitud', 'detail': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
