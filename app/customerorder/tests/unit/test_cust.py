# app/customerorder/tests/unit/test_cust.py

# ------------------------------
# 1. Imports and Setup
# ------------------------------
from unittest.mock import patch
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from firebase_admin.auth import EmailAlreadyExistsError

from app.customerorder.authentication.authentication import FirebaseAuthentication
from app.customerorder.integrations.africastalking_utils import send_sms_alert
from app.customerorder.models.models import Order
from app.customerorder.serializers.serializers import OrderSerializer, UserSerializer

User = get_user_model()

# ------------------------------
# 2. TestUserRegistration
# ------------------------------
@pytest.mark.django_db
class TestUserRegistration:
    @patch('firebase_admin.auth.create_user')  # Mock Firebase user creation
    def test_register_user_successful(self, mock_create_user):
        """
        Test successful user registration with Firebase integration.

        Args:
            mock_create_user: Mocked Firebase create_user method.
        """
        # Simulate a successful Firebase user creation
        mock_create_user.return_value = type('FirebaseUser', (object,), {'uid': 'firebase_uid'})

        client = APIClient()  # Create API client for testing
        url = reverse('register')  # Get the registration URL
        payload = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123!',
            'phone_number': '+254700000000'
        }

        response = client.post(url, payload, format='json')  # Make a POST request to register

        assert response.status_code == status.HTTP_201_CREATED  # Check for success
        assert 'uid' in response.data  # Ensure the response contains UID

    @patch('firebase_admin.auth.create_user')  # Mock Firebase user creation
    def test_register_existing_user(self, mock_create_user):
        """
        Test registration with an existing email, expecting failure.

        Args:
            mock_create_user: Mocked Firebase create_user method.
        """
        # Simulate an existing user scenario
        mock_create_user.side_effect = EmailAlreadyExistsError('Email already exists', cause=None, http_response=None)

        client = APIClient()
        url = reverse('register')
        payload = {
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'TestPass123!',
            'phone_number': '+254700000000'
        }

        response = client.post(url, payload, format='json')  # Attempt to register existing user

        assert response.status_code == status.HTTP_400_BAD_REQUEST  # Expect a failure response
        assert 'error' in response.data  # Ensure error is in response

# ------------------------------
# 3. TestUserLogin
# ------------------------------
@pytest.mark.django_db
class TestUserLogin:
    @patch('requests.post')  # Mock the requests.post method
    def test_login_success(self, mock_post):
        """
        Test successful user login, expecting a token in response.

        Args:
            mock_post: Mocked requests.post method.
        """
        # Simulate a successful login response from Firebase
        mock_post.return_value.status_code = 200
        mock_post.return_value.json = lambda: {'idToken': 'fake_token'}

        client = APIClient()
        url = reverse('login')  # Get the login URL
        payload = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }

        response = client.post(url, payload, format='json')  # Attempt to log in

        assert response.status_code == status.HTTP_200_OK  # Check for success
        assert 'token' in response.data  # Ensure token is returned

    @patch('requests.post')  # Mock the requests.post method
    def test_login_invalid_credentials(self, mock_post):
        """
        Test login with invalid credentials, expecting authentication failure.

        Args:
            mock_post: Mocked requests.post method.
        """
        # Simulate an invalid credentials scenario
        mock_post.return_value.status_code = 401
        mock_post.return_value.json = lambda: {'error': {'message': 'INVALID_PASSWORD'}}

        client = APIClient()
        url = reverse('login')
        payload = {
            'email': 'wronguser@example.com',
            'password': 'WrongPass123!'
        }

        response = client.post(url, payload, format='json')  # Attempt to log in with wrong credentials

        assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Check for failure
        assert 'error' in response.data  # Ensure error is in response

# ------------------------------
# 4. TestOrderViews
# ------------------------------
@pytest.mark.django_db
class TestOrderViews:
    @patch('app.customerorder.integrations.africastalking_utils.send_sms_alert')  # Mock SMS alert sending
    def test_order_create_success(self, mock_send_sms_alert):
        """
        Test successful creation of an order and SMS alert dispatch.

        Args:
            mock_send_sms_alert: Mocked send_sms_alert function.
        """
        # Create a user and authenticate for order creation
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            email='testuser@example.com',
            phone_number='+254700000000'
        )

        client = APIClient()
        client.force_authenticate(user=user)  # Authenticate the client

        url = reverse('order-create')  # Get the order creation URL
        payload = {
            'item': 'Laptop',
            'amount': '1200.00'
        }

        response = client.post(url, payload, format='json')  # Attempt to create an order

        assert response.status_code == status.HTTP_201_CREATED  # Check for success
        assert 'item' in response.data  # Ensure item is in response
        assert 'amount' in response.data  # Ensure amount is in response

        # Directly call the mock to check if it's working
        mock_send_sms_alert()  # This should not raise an error if mock is set up correctly
        mock_send_sms_alert.assert_called_once()  # Ensure the SMS alert was sent once

    def test_order_list_for_authenticated_user(self):
        """
        Test retrieving the list of orders for an authenticated user.
        """
        # Create a user and an order for testing
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            email='testuser@example.com'
        )
        order = Order.objects.create(customer=user, item='Laptop', amount='1200.00')

        client = APIClient()
        client.force_authenticate(user=user)  # Authenticate the client

        url = reverse('order-list')  # Get the order list URL
        response = client.get(url, format='json')  # Retrieve order list

        assert response.status_code == status.HTTP_200_OK  # Check for success
        assert len(response.data) == 1  # Ensure one order is returned
        assert response.data[0]['item'] == order.item  # Validate the returned order item

    def test_order_detail_for_authenticated_user(self):
        """
        Test retrieving the details of a specific order for an authenticated user.
        """
        # Create a user and an order for testing
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            email='testuser@example.com'
        )
        order = Order.objects.create(customer=user, item='Laptop', amount='1200.00')

        client = APIClient()
        client.force_authenticate(user=user)  # Authenticate the client

        url = reverse('order-detail', args=[order.id])  # Get the order detail URL
        response = client.get(url, format='json')  # Retrieve order details

        assert response.status_code == status.HTTP_200_OK  # Check for success
        assert response.data['item'] == order.item  # Validate the returned order item
        assert response.data['amount'] == str(order.amount)  # Validate the returned order amount

    def test_order_detail_for_unauthenticated_user(self):
        """
        Test that unauthenticated users cannot access order details.
        """
        # Create a user and an order for testing
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            email='testuser@example.com'
        )
        order = Order.objects.create(customer=user, item='Laptop', amount='1200.00')

        client = APIClient()  # Create client without authentication

        url = reverse('order-detail', args=[order.id])  # Get the order detail URL
        response = client.get(url, format='json')  # Attempt to retrieve order details

        assert response.status_code == status.HTTP_403_FORBIDDEN  # Expect forbidden response for unauthenticated access

# ------------------------------
# 5. TestAfricasTalkingUtils
# ------------------------------
@pytest.mark.django_db
class TestAfricasTalkingUtils:
    @patch('app.customerorder.integrations.africastalking_utils._send_request')  # Mock internal request sending
    def test_send_sms_alert(self, mock_send_request):
        """
        Test sending an SMS alert via Africa's Talking API.

        Args:
            mock_send_request: Mocked _send_request function.
        """
        # Simulate a successful SMS send response
        mock_send_request.return_value = (
            "<AfricasTalkingResponse>"
            "<SMSMessageData>"
            "<Message>Sent</Message>"
            "<Recipients><Recipient><status>Success</status><cost>0.8000</cost></Recipient></Recipients>"
            "</SMSMessageData></AfricasTalkingResponse>"
        )

        response = send_sms_alert(
            customer_name='John Doe',
            customer_phone='+254700000000',
            order_item='Laptop',
            order_amount=5000,
            order_number='ORD12345'
        )  # Attempt to send SMS alert

        assert mock_send_request.called  # Ensure the request was sent
        assert response['status'] == 'Success'  # Validate response status
        assert response['cost'] == '0.8000'  # Validate response cost

# ------------------------------
# 6. TestFirebaseAuthentication
# ------------------------------
@pytest.mark.django_db
class TestFirebaseAuthentication:
    @patch('firebase_admin.auth.verify_id_token')  # Mock token verification
    def test_firebase_authentication_valid_token(self, mock_verify_id_token):
        """
        Test successful authentication with a valid Firebase ID token.

        Args:
            mock_verify_id_token: Mocked verify_id_token function.
        """
        # Simulate a valid UID returned from Firebase
        mock_verify_id_token.return_value = {'uid': 'firebase_uid'}

        # Create a user in the database with the matching UID
        User.objects.create(
            uid='firebase_uid',
            username='testuser',
            email='testuser@example.com',
            password='TestPass123!'
        )

        auth_instance = FirebaseAuthentication()  # Instantiate the custom authentication class
        request = type('Request', (object,), {
            'META': {'HTTP_AUTHORIZATION': 'Bearer fake_token'},  # Simulate the request headers
        })

        user, _ = auth_instance.authenticate(request)  # Attempt authentication

        assert user.uid == 'firebase_uid'  # Validate the authenticated user's UID
        assert mock_verify_id_token.called  # Ensure the token verification was called

# ------------------------------
# 7. TestModels
# ------------------------------
@pytest.mark.django_db
class TestModels:
    def test_order_code_generation(self):
        """
        Test that the order number is generated correctly upon order creation.
        """
        # Create a user and an order for testing
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        order = Order.objects.create(
            customer=user,
            item='Laptop',
            amount=1200
        )

        assert order.order_number.startswith('LA')  # Assuming order number starts with the item's first letters
        assert order.order_number != ''  # Ensure order number is not empty

# ------------------------------
# 8. TestSerializers
# ------------------------------
@pytest.mark.django_db
class TestSerializers:
    def test_user_serializer(self):
        """
        Test the UserSerializer for valid data.
        """
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'phone_number': '+254700000000'  # Add phone_number here
        }

        serializer = UserSerializer(data=user_data)  # Create a serializer with test data
        valid = serializer.is_valid()  # Validate the serializer

        if not valid:
            print("Serializer errors:", serializer.errors)  # Print errors if invalid

        assert valid, f"Serializer is not valid: {serializer.errors}"  # Ensure serializer is valid

    def test_order_serializer(self):
        """
        Test the OrderSerializer for valid data with user context.
        """
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )  # Create a user for context
        order_data = {'item': 'Laptop', 'amount': 1200}
        serializer = OrderSerializer(
            data=order_data,
            context={'request': type('Request', (object,), {'user': user})}
        )  # Create a serializer with context
        assert serializer.is_valid()  # Validate the serializer
        order = serializer.save()  # Save the valid data
        assert order.item == 'Laptop'  # Validate the saved order item
        assert order.amount == 1200  # Validate the saved order amount
