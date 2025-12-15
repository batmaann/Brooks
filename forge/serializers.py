from django.db import models
from rest_framework import serializers
from forge import models

class Vehicle(serializers.ModelSerializer):
    class Meta:
        model = models.Vehicle
        fields ='__all__'