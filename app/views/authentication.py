import os
import random
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from ..baserow_client.user import User
from baserowapi import Filter
import datetime
from django.core.mail import send_mail
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from ..forms.authentication import RequestCodePostForm

@api_view(['POST'])
def request_code(request):
    form = RequestCodePostForm(request.data)
    if not form.is_valid():
        return Response({"message": "Invalid data", "errors": form.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    email = request.data.get('email')
    # Check if email exists
    user = User.table.get_rows(filters=[Filter("email", email)], return_single=True)
    if not user:
        return Response({"message": "Email not found"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Generate code
    num = random.randint(0, 9999)
    code = str(num).zfill(4)


    # Generate datetime 5 minutes from now
    five_minutes_from_now = datetime.datetime.now() + datetime.timedelta(minutes=5)

    # Update user
    user.update({"auth_code": code, "auth_expiry": five_minutes_from_now})

    if os.environ.get('APP_ENV') != 'test':
        send_mail(
            "Company Inventory Login Code",
            code,
            "noreply@mail.kimpalao.com",
            [email],
        )

    response_data = {"message": "Code sent"}

    if settings.DEBUG:
        response_data["code"] = code

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    user = request.user
    user.auth_token.delete()

    return Response({}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    return Response({"email": user.email, 'role': user.role.role}, status=status.HTTP_200_OK)