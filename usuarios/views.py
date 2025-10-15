from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from .forms import RegistroForm, LoginForm
from .models import Usuario
import requests
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            # Validar contraseñas
            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
            else:
                # Consumir servicio externo
                url = 'https://asiricarritos.onrender.com/registro/'
                data = {
                    'nombre': nombre,
                    'correo': correo,
                    'password': password1,
                    'rol': 'usuario'
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

