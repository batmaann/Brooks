from django.contrib import admin

from users import models


@admin.register(models.Users)
class UsersAdmin(admin.ModelAdmin):
    pass


