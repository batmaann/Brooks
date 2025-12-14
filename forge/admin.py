from django.contrib import admin
from django.core.checks import register

# Register your models here.
from forge import models


@admin.register(models.GasStation)
class GasStation(admin.ModelAdmin):
    pass


@admin.register(models.Vehicle)
class Vehicle(admin.ModelAdmin):
    pass


@admin.register(models.Refueling)
class Refueling(admin.ModelAdmin):
    pass


@admin.register(models.FuelPrice)
class FuelPrice(admin.ModelAdmin):
    pass


@admin.register(models.FuelStatistics)
class FuelStatistics(admin.ModelAdmin):
    pass
