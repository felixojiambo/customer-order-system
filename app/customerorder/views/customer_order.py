# ------------------------------
# 1. Imports and Logger Setup
# ------------------------------
import requests
import logging
from django.conf import settings
from firebase_admin import auth as firebase_auth
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError  # Add this import

from app.customerorder.authentication.authentication import FirebaseAuthentication
from app.customerorder.integrations.africastalking_utils import send_sms_alert
from app.customerorder.models.models import Order, User
from app.customerorder.serializers.serializers import UserSerializer, OrderSerializer

logger = logging.getLogger(__name__)

#------------------------------
#2. RegisterView
#------------------------------
class RegisterView(generics.CreateAPIView):
    """
    API view for user registration. Creates a Firebase user and saves them in the local database.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs) -> Response:
        """
        Create a new user in Firebase and save their details locally.

        Args:
            request: The HTTP request containing user registration data.

        Returns:
            Response: The HTTP response indicating success or failure.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        phone_number = serializer.validated_data.get('phone_number')

        try:
            firebase_user = firebase_auth.create_user(email=email, password=password)

            user = User(
                username=request.data['username'],
                email=email,
                phone_number=phone_number,
                uid=firebase_user.uid
            )
            user.save()

            logger.info(f"User registered: {email}")
            return Response({"uid": firebase_user.uid, "email": email}, status=status.HTTP_201_CREATED)

        except firebase_auth.EmailAlreadyExistsError:
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({"error": "An error occurred during registration."}, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------
# 7. HealthCheckView
# ------------------------------
class HealthCheckView(generics.GenericAPIView):
    """
    API view for health check. Returns a simple success response.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs) -> Response:
        """
        Responds with a success message to indicate the server is running.

        Args:
            request: The HTTP GET request.

        Returns:
            Response: A success message with a 200 OK status.
        """
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]
#
#     def create(self, request, *args, **kwargs) -> Response:
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         try:
#             email = serializer.validated_data['email']
#             password = serializer.validated_data['password']
#             phone_number = serializer.validated_data.get('phone_number')
#
#             # Firebase user creation
#             firebase_user = firebase_auth.create_user(email=email, password=password)
#             user = User(
#                 username=serializer.validated_data['username'],
#                 email=email,
#                 phone_number=phone_number,
#                 uid=firebase_user.uid
#             )
#             user.save()
#
#             logger.info(f"User registered successfully: {email}")
#             return Response({"uid": firebase_user.uid, "email": email}, status=status.HTTP_201_CREATED)
#
#         except firebase_auth.EmailAlreadyExistsError:
#             raise ValidationError({"email": "A user with this email already exists."})
#         except Exception as e:
#             logger.error(f"Registration error: {str(e)}")
#             raise ValidationError({"error": f"Registration failed: {str(e)}"})

# ------------------------------
# 3. LoginView
# ------------------------------
class LoginView(generics.GenericAPIView):
    """
    API view for user login via Firebase. Returns a Firebase token upon successful authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        """
        Authenticate the user with Firebase and return an ID token.

        Args:
            request: The HTTP request containing login credentials.

        Returns:
            Response: The HTTP response with an ID token or an error message.
        """
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"User login attempt: {email}")

        try:
            firebase_auth_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
            api_key = settings.FIREBASE_API_KEY

            payload = {
                'email': email,
                'password': password,
                'returnSecureToken': True
            }

            response = requests.post(f"{firebase_auth_url}?key={api_key}", json=payload)

            if response.status_code == 200:
                token_data = response.json()
                id_token = token_data['idToken']

                logger.info(f"User logged in successfully: {email}")
                return Response({'token': id_token}, status=status.HTTP_200_OK)
            else:
                error_message = response.json().get('error', {}).get('message', 'Authentication failed.')
                logger.warning(f"Login failed for {email}: {error_message}")
                return Response({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during login: {str(e)}")
            return Response({'error': 'An error occurred while attempting to login.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------------------
# 4. OrderCreateView
# ------------------------------
class OrderCreateView(generics.CreateAPIView):
    """
    API view to create a new order for the authenticated user.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseAuthentication]

    def perform_create(self, serializer) -> None:
        """
        Automatically associate the order with the authenticated user and send an SMS alert.

        Args:
            serializer: The serializer instance with validated data for the new order.
        """
        order = serializer.save(customer=self.request.user)

        send_sms_alert(
            customer_name=order.customer.username,
            customer_phone=order.customer.phone_number,
            order_item=order.item,
            order_amount=order.amount,
            order_number=order.order_number
        )

# ------------------------------
# 5. OrderDetailView
# ------------------------------
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific order for the authenticated user.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseAuthentication]

    def get_queryset(self):
        """
        Filter orders to only include those belonging to the authenticated user.

        Returns:
            QuerySet: Filtered queryset for the authenticated user.
        """
        return self.queryset.filter(customer=self.request.user)

# ------------------------------
# 6. OrderListView
# ------------------------------
class OrderListView(generics.ListAPIView):
    """
    API view to list all orders for the authenticated user.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseAuthentication]

    def get_queryset(self):
        """
        Return orders for the authenticated user.

        Returns:
            QuerySet: Filtered queryset of orders for the authenticated user.
        """
        return self.queryset.filter(customer=self.request.user)
