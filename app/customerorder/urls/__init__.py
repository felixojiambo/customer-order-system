
from django.urls import path, include

urlpatterns = [
    path('', include('app.customerorder.urls.urls')),  
]
