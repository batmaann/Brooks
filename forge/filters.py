from forge import models
import django_filters


class Vehicle(django_filters.FilterSet):
    class Meta:
        model = models.Vehicle
        fields = '__all__'
