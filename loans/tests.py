from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from customers.models import Customer
from .models import Loan

class LoanTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name='John', last_name='Doe', age=35, phone_number=9999999999,
            monthly_salary=60000, approved_limit=round(36 * 60000, -5)
        )

    def test_check_eligibility(self):
        payload = {
            "customer_id": self.customer.id,
            "loan_amount": 100000,
            "interest_rate": 14.0,
            "tenure": 12
        }
        response = self.client.post(reverse('check-eligibility'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)

    def test_create_loan(self):
        payload = {
            "customer_id": self.customer.id,
            "loan_amount": 100000,
            "interest_rate": 14.0,
            "tenure": 12
        }
        response = self.client.post(reverse('create-loan'), payload, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertIn('loan_approved', response.data)
