import random
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..baserow_client import users_table
from baserowapi import Filter
import datetime
from django.core.mail import send_mail

@api_view(['POST'])
def request_code(request):
    email = request.data.get('email')
    # Check if email exists
    user = users_table.get_rows(filter=Filter("email", email), return_single=True)
    if not user:
        return Response({"message": "Email not found"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Generate code
    num = random.randint(0, 9999)
    code = str(num).zfill(4)


    # Generate datetime 5 minutes from now
    five_minutes_from_now = datetime.datetime.now() + datetime.timedelta(minutes=5)

    # Update user
    user.update({"auth_code": code, "auth_expiry": five_minutes_from_now})

    send_mail(
        "Company Inventory Login Code",
        code,
        "noreply@mail.kimpalao.com",
        [email],
    )

    return Response({"message": "Code sent"}, status=status.HTTP_200_OK)
