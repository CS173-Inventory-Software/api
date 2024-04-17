from django.db import models
from django.contrib.auth.models import User
from .baserow_client.user import UserTypeEnum

# Create your models here.
class Role(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.IntegerField(default=UserTypeEnum.VIEWER.value)