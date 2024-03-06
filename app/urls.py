from django.urls import path
from rest_framework.authtoken import views
from .authentication import CustomAuthToken
from .views import authentication, hardware

urlpatterns = [
    path('login/', CustomAuthToken.as_view()),
    path('request-code/', authentication.request_code),
    path('get-user/', authentication.get_user),

    # Hardware
    path('hardware/', hardware.HardwareList.as_view()),
]
