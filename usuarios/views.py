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
        # Detectar si la petición es JSON
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'JSON inválido', 'detail': str(e)}, status=400)
            nombre = data.get('nombre')
            correo = data.get('correo')
            password = data.get('password')
            rol = data.get('rol', 'usuario')
            # Validar campos
            if not all([nombre, correo, password]):
                return JsonResponse({'success': False, 'error': 'Faltan campos obligatorios.'}, status=400)
            # Consumir servicio externo
            url = 'https://asiricarritos.onrender.com/registro/'
            payload = {
                'nombre': nombre,
                'correo': correo,
                'password': password,
                'rol': rol
            }
            try:
                response = requests.post(url, data=payload)
                if response.status_code == 201:
                    return JsonResponse({'success': True, 'message': 'Usuario registrado correctamente.'}, status=201)
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=response.status_code)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'Error de conexión', 'detail': str(e)}, status=500)
        else:
            # Procesar formulario tradicional
            form = RegistroForm(request.POST)
            if form.is_valid():
                nombre = form.cleaned_data['nombre']
                correo = form.cleaned_data['correo']
                password = form.cleaned_data['password']
                rol = form.cleaned_data.get('rol', 'usuario')
                url = 'https://asiricarritos.onrender.com/registro/'
                data = {
                    'nombre': nombre,
                    'correo': correo,
                    'password': password,
                    'rol': rol
                }
                try:
                    response = requests.post(url, data=data)
                    if response.status_code == 201:
                        messages.success(request, 'Usuario registrado correctamente.')
                        return redirect('login')
                    else:
                        messages.error(request, f'Error al registrar: {response.text}')
                except Exception as e:
                    messages.error(request, f'Error de conexión: {str(e)}')
            # Si no es válido, mostrar errores en el formulario
            return render(request, 'usuarios/registro.html', {'form': form})
    else:
        form = RegistroForm()
        return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            password = form.cleaned_data['password']
            usuario = authenticate(request, correo=correo, password=password)
            if usuario is not None:
                login(request, usuario)
                usuario.fechaultimoingreso = timezone.now()
                usuario.save()
                return redirect('home')
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'usuarios/home.html')
