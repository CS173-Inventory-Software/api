from django.urls import path
from rest_framework.authtoken import views
from .authentication import CustomAuthToken

urlpatterns = [
    path('login/', CustomAuthToken.as_view())
]
