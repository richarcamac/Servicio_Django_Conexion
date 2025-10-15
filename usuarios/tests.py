from django.test import TestCase, Client
from django.urls import reverse
import json

class RegistroAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('registro')

    def test_registro_json(self):
        payload = {
            'nombre': 'Test User',
            'correo': 'testuser@example.com',
            'password': 'testpassword123',
            'rol': 'USER',
            'status': True
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Usuario registrado correctamente', response.json().get('message', ''))

    def test_registro_faltan_campos(self):
        payload = {
            'nombre': 'Test User',
            'correo': 'testuser2@example.com'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Faltan campos obligatorios', response.json().get('error', ''))

