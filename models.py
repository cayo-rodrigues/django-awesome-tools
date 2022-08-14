from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class CustomAbstractUser(AbstractUser):
    username = None
    USERNAME_FIELD = "email"
    objects = CustomUserManager()
