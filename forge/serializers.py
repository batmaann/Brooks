from django.db import models
from rest_framework import serializers
from forge import models


class Vehicle(serializers.ModelSerializer):
    class Meta:
        model = models.Vehicle
        exclude = ['license_plate']


class Refueling(serializers.ModelSerializer):
    class Meta:
        model = models.Refueling
        fields = '__all__'


class FuelStatistics(serializers.ModelSerializer):
    class Meta:
        model = models.FuelStatistics
        fields = '__all__'


class GasStation(serializers.ModelSerializer):
    class Meta:
        model = models.GasStation
        fields = '__all__'
