from django.urls import path
from rest_framework.authtoken import views
from .authentication import CustomAuthToken
from .views import authentication, hardware, status, hardware_instance

urlpatterns = [
    path('login/', CustomAuthToken.as_view()),
    path('request-code/', authentication.request_code),
    path('get-user/', authentication.get_user),

    # Hardware
    path('hardware/', hardware.HardwareList.as_view()),
    path('hardware/<int:pk>/', hardware.HardwareDetail.as_view()),

    path('hardware-instance/', hardware_instance.HardwareInstanceList.as_view()),

    # Status
    path('status/', status.StatusList.as_view()),
]
