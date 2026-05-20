from django.conf import settings
from django.db import models


class Users(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='users'
    )

    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    def __str__(self):
        return f"Профиль для {self.user.username}"
