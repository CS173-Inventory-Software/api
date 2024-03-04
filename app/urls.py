from django.urls import path
from rest_framework.authtoken import views
from .authentication import CustomAuthToken
from .views import auth

urlpatterns = [
    path('login/', CustomAuthToken.as_view()),
    path('request-code/', auth.request_code)
]
