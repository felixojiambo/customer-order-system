from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

User = get_user_model()
"""
Retrieve the custom user model.
"""

from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model with custom customer details and validation.
    """
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer_details', 'item', 'order_number', 'amount', 'status', 'created_at']

    def get_customer_details(self, obj):
        """
        Returns customer details for the order.
        """
        user = obj.customer
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }

    def validate_amount(self, value):
        """
        Validates that the order amount is greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data):
        """
        Override create method to handle order creation with the authenticated user.
        """
        validated_data.pop('customer', None)
        user = self.context['request'].user
        order = Order.objects.create(customer=user, **validated_data)
        return order

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model with email, username validation, and password handling.
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

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        """
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
