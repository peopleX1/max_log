from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(verbose_name="Phone number", max_length=20, unique=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f'User: {self.id} | {self.username}'

    def get_phone(self):
        return str(self.phone)
