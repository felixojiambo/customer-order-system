from django.urls import path
from app.customerorder.views.customer_order import RegisterView, LoginView, OrderListView, OrderCreateView, \
    OrderDetailView,HealthCheckView

urlpatterns = [
    # URLs for Customer
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    # Health check route # Health Check endpoint
    path('health', HealthCheckView.as_view(), name='health-check'),
]
