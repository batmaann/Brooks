from django.contrib import admin
from django.contrib import admin
from django.core.checks import register


from users import models


@admin.register(models.Users)
class UsersAdmin(admin.ModelAdmin):
    pass


