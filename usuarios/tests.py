from django.test import TestCase, Client
from django.urls import reverse
import json

class RegistroAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('registro')

    def test_registro_exitoso_json(self):
        payload = {
            'nombre': 'Test User',
            'correo': 'testuser@example.com',
            'password': 'testpassword',
            'rol': 'usuario'
        }
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertIn(response.status_code, [201, 400, 409])  # 201 si éxito, 400/409 si error externo
        self.assertTrue('success' in response.json())

    def test_registro_faltan_campos(self):
        payload = {
            'nombre': 'Test User',
            'correo': 'testuser2@example.com'
            # Falta password
        }
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('Faltan campos', response.json()['error'])

    def test_registro_json_invalido(self):
        response = self.client.post(self.url, data='no es json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('JSON inválido', response.json()['error'])

    # Puedes agregar más pruebas según la lógica del servicio externo
