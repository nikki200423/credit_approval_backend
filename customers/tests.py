from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Customer

class CustomerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "age": 30,
            "monthly_income": 50000,
            "phone_number": 9876543210
        }

    def test_register_customer(self):
        response = self.client.post(reverse('register-customer'), self.customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().first_name, 'Alice')
