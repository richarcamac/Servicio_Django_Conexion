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

@csrf_exempt
def registro_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'JSON inválido', 'detail': str(e)}, status=400)
            form = RegistroForm(data)
        else:
            form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                return JsonResponse({'success': True, 'message': 'Usuario registrado correctamente.'}, status=201)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'Error al guardar usuario', 'detail': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Datos inválidos', 'detail': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'JSON inválido', 'detail': str(e)}, status=400)
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
                return JsonResponse({'success': False, 'error': 'Error en login', 'detail': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Datos inválidos', 'detail': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'usuarios/home.html')
