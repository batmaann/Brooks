from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Users(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, blank=False, verbose_name="Телефон")

    def __str__(self):
        return f" {self.user.username}"
