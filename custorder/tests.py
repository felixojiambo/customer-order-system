from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Customer, Order

# Model Tests
class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="John Doe", code="C001")

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.code, "C001")


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="John Doe", code="C001")
        self.order = Order.objects.create(customer=self.customer, item="Laptop", amount=1000.00)

    def test_order_creation(self):
        self.assertEqual(self.order.item, "Laptop")
        self.assertEqual(self.order.amount, 1000.00)
        self.assertEqual(self.order.customer.name, "John Doe")


# API Tests
class CustomerAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_data = {'name': 'Jane Doe', 'code': 'C002'}

    def test_create_customer(self):
        response = self.client.post(reverse('customer-list'), self.customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Additional assertions
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().name, 'Jane Doe')


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(name="John Doe", code="C001")
        self.order_data = {'customer': self.customer.id, 'item': 'Phone', 'amount': 500.00}

    def test_create_order(self):
        response = self.client.post(reverse('order-list'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Additional assertions
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.item, 'Phone')
        self.assertEqual(order.amount, 500.00)

    # Negative test for missing fields
    def test_create_order_missing_fields(self):
        invalid_data = {'item': 'Phone'}
        response = self.client.post(reverse('order-list'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Negative test for unauthorized access (if you implement OAuth later)
    def test_create_order_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = self.client.post(reverse('order-list'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
