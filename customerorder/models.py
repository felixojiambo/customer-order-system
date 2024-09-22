from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Max
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model extending AbstractUser with additional fields.
    """
    phone_number = models.CharField(max_length=15, unique=True)
    uid = models.CharField(max_length=255, unique=True, blank=True, null=True)
    customer_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        """
        Returns the string representation of the user.
        """
        return self.username

    def save(self, *args, **kwargs):
        """
        Override save to generate customer code if not provided.
        """
        if not self.customer_code:
            self.code = self.generate_customer_code()
        super().save(*args, **kwargs)

    def generate_customer_code(self):
        """
        Generates a unique customer code in the format of CUST<timestamp><incrementing_number>.
        """
        now = timezone.now()
        base_code = f"CUST{now.strftime('%Y%m%d%H%M%S')}"
        current_max = User.objects.aggregate(Max('code'))
        current_count = int(current_max['code__max'][-2:]) + 1 if current_max['code__max'] else 1
        return f"{base_code}{current_count:02d}"

class OrderStatus(models.TextChoices):
    """
    Enum for order status options.
    """
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    CANCELED = 'Canceled'

class Order(models.Model):
    """
    Order model representing customer orders.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    item = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        """
        Returns the string representation of the order.
        """
        return f"{self.item} - {self.customer.username}"

    def save(self, *args, **kwargs):
        """
        Override save to generate order number if not provided.
        """
        if not self.order_number:
            self.order_number = generate_order_code(self.item)
        super().save(*args, **kwargs)

def generate_order_code(item):
    """
    Generate a unique order code based on the item and current timestamp.
    """
    now = timezone.now()
    base_code = f"{item[:2].upper()}{now.strftime('%Y%m%d%H%M%S')}"
    current_max = Order.objects.filter(
        created_at__year=now.year,
        created_at__month=now.month,
        created_at__day=now.day,
        created_at__hour=now.hour,
        created_at__minute=now.minute,
        created_at__second=now.second
    ).aggregate(Max('order_number'))
    current_count = int(current_max['order_number__max'][-2:]) + 1 if current_max['order_number__max'] else 1
    return f"{base_code}{current_count:02d}"
