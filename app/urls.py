from django.urls import path
from rest_framework.authtoken import views
from .authentication import CustomAuthToken
from .views import authentication, hardware, status, hardware_instance, software, software_instance, user, user_type, reports

urlpatterns = [
    path('login/', CustomAuthToken.as_view()),
    path('logout/', authentication.logout),
    path('request-code/', authentication.request_code),
    path('get-user/', authentication.get_user),
    path('user/hardware/', user.UserAssignedHardware.as_view()),
    path('user/software/', user.UserAssignedSoftware.as_view()),

    # Hardware
    path('hardware/', hardware.HardwareList.as_view()),
    path('hardware/<int:pk>/', hardware.HardwareDetail.as_view()),

    path('hardware-instance/', hardware_instance.HardwareInstanceList.as_view()),

    path('hardware-csv/', hardware_instance.HardwareCSV.as_view()),
    path('hardware-json/', hardware_instance.HardwareJSON.as_view()),

    # Software
    path('software/', software.SoftwareList.as_view()),
    path('software/<int:pk>/', software.SoftwareDetail.as_view()),
    path('software-instance/', software_instance.SoftwareInstanceList.as_view()),

    path('software-csv/', software_instance.SoftwareCSV.as_view()),
    path('software-json/', software_instance.SoftwareJSON.as_view()),

    # Status
    path('status/', status.StatusList.as_view()),

    # Users
    path('users/', user.UserList.as_view()),
    path('users/<int:pk>/', user.UserDetail.as_view()),

    # User Types
    path('user-types/', user_type.UserTypeList.as_view()),
    
    # Reports
    path('reports/software-near-expiry/', reports.SoftwareNearExpiry.as_view()),
    path('reports/hardware-needing-maintenance/', reports.HardwareNeedingMaintenance.as_view()),
    path('reports/hardware-not-assigned/', reports.HardwareNotAssigned.as_view()),
    path('reports/software-not-assigned/', reports.SoftwareNotAssigned.as_view()),
]
