
import datetime
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .baserow_client.user import User
from baserowapi import Filter
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Role


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("email"),
        write_only=True
    )
    code = serializers.CharField(
        label=_("code"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        now = datetime.datetime.now()
        email = attrs.get('email')
        code = attrs.get('code')

        if email and code:
            user = User.table.get_rows(filters=[Filter("email", email)], return_single=True)

            if not user or code != user['auth_code']:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            expiry = datetime.datetime.strptime(user['auth_expiry'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if now > expiry:
                msg = _('Code has expired.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "passcode".')
            raise serializers.ValidationError(msg, code='authorization')

        # check if the user exists in the django db

        try:
            django_user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            django_user = User.objects.create_user(username=email, email=email, password="")

        Role.objects.update_or_create({'role': user.values['type'].id}, user=django_user)

        attrs['user'] = django_user
        return attrs


class CustomAuthToken(ObtainAuthToken):

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'email': user.email
        })

