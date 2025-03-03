from ..models import User, LoginAttempt
from datetime import datetime, timedelta
from rest_framework.test import APITestCase
from django.urls import reverse
from django.test  import Client
import json
from django.db import connection
from .sql_queries import (
    SQL_CREATE_SCHEMA,
    SQL_PG_CRYPTO,
    SQL_USER,
    SQL_COPMPARE_PW,
    SQL_CYPHER,
    SQL_INSUPDATE,
    SQL_LOGIN
)

class BruteForceTest(APITestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('loginReact')
        with connection.cursor() as cursor:
            cursor.execute(SQL_CREATE_SCHEMA)
            cursor.execute(SQL_PG_CRYPTO)
            cursor.execute(SQL_USER)
            cursor.execute(SQL_COPMPARE_PW)
            cursor.execute(SQL_CYPHER)
            cursor.execute(SQL_INSUPDATE)
            cursor.execute(SQL_LOGIN)

    def test_01_register_and_login(self):
        user_data = {'user_name': 'cesar', 'password': '123'}
        response = self.client.post(reverse('registerReact'), data=json.dumps(user_data), content_type='application/json')
        print(json.dumps(response.json(), indent=2))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        
        user_data = {'user_name': 'cesar', 'password': '123'}
        response = self.client.post(reverse('loginReact'), data=json.dumps(user_data), content_type='application/json')
        print(json.dumps(response.json(), indent=2))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
    
    def test_02_register_brute_force(self):
        user_data = {'user_name': 'cesar', 'password': '123'}
        self.client.post(reverse('registerReact'), data=json.dumps(user_data), content_type='application/json')

        # Simulate brute force login attempts
        passwords = ['wrong_password1', 'wrong_password2', 'wrong_password3','wrong_password1', 'wrong_password2', 'wrong_password3',
                     'wrong_password1', 'wrong_password2', 'wrong_password3','wrong_password1', 'wrong_password2', 'wrong_password3',
                     'wrong_password1', 'wrong_password2', 'wrong_password3','wrong_password1', 'wrong_password2', 'wrong_password3']
        for password in passwords:
            user_data = {'user_name': 'cesar', 'password': password}
            response = self.client.post(reverse('loginReact'), data=json.dumps(user_data), content_type='application/json')
            print(json.dumps(response.json(), indent=2))
            if response.status_code == '429':
                self.assertEqual(response.status_code, 429)
                self.assertEqual(response.json()['success'], True)
                return