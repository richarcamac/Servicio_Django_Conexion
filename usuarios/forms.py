from django import forms
from .models import Usuario

class RegistroForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    correo = forms.CharField(max_length=50)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, max_length=128)
    rol = forms.CharField(max_length=20)
    status = forms.BooleanField(required=False)

    def save(self, commit=True):
        usuario = Usuario(
            nombre=self.cleaned_data['nombre'],
            correo=self.cleaned_data['correo'],
            rol=self.cleaned_data['rol'],
            status=self.cleaned_data.get('status', True)
        )
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario

class LoginForm(forms.Form):
    correo = forms.EmailField(label='Correo')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
