# ------------------------------
# 1. Imports and User Model Retrieval
# ------------------------------
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from app.customerorder.models.models import Order

User = get_user_model()
"""
Retrieve the custom user model to use in serializers.
"""

# ------------------------------
# 2. OrderSerializer
# ------------------------------
class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model with custom customer details and validation.

    Attributes:
        customer_details (SerializerMethodField): Custom field for displaying user details.
    """
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer_details', 'item', 'order_number', 'amount', 'status', 'created_at']

    def get_customer_details(self, obj) -> dict:
        """
        Returns customer details for the order.

        Args:
            obj (Order): The order instance.

        Returns:
            dict: Dictionary with customer details.
        """
        user = obj.customer
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }

    def validate_amount(self, value: float) -> float:
        """
        Validates that the order amount is greater than zero.

        Args:
            value (float): The order amount to validate.

        Raises:
            serializers.ValidationError: If amount is not greater than zero.

        Returns:
            float: The validated amount.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data: dict) -> Order:
        """
        Override create method to handle order creation with the authenticated user.

        Args:
            validated_data (dict): The validated data from the request.

        Returns:
            Order: The created Order instance.
        """
        validated_data.pop('customer', None)
        user = self.context['request'].user
        order = Order.objects.create(customer=user, **validated_data)
        return order

# ------------------------------
# 3. UserSerializer
# ------------------------------
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model with email, username validation, and password handling.

    Attributes:
        email (EmailField): Required email field with uniqueness validator.
        username (CharField): Required username field with uniqueness validator.
        password (CharField): Write-only password field for creating user with hashed password.
        customer_code (CharField): Read-only customer code field.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    customer_code = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'customer_code']

    def create(self, validated_data: dict) -> User:
        """
        Create a new user with a hashed password.

        Args:
            validated_data (dict): The validated data from the request.

        Returns:
            User: The created User instance.
        """
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
