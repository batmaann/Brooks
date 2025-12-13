from django.contrib import admin
from django.core.checks import register

# Register your models here.
from forge import models


@admin.register(models.GasStation)
class GasStation(admin.ModelAdmin):
    pass