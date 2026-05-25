from django.db import models
from rest_framework import serializers
from forge import models


class Vehicle(serializers.ModelSerializer):
    current_odometer = serializers.IntegerField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Vehicle
        exclude = ['license_plate']
        read_only_fields = ['current_odometer', 'user']

    def create(self, validated_data):
        """Автоматически устанавливаем текущего пользователя"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Не даем изменить владельца"""
        validated_data.pop('user', None)
        return super().update(instance, validated_data)

    def validate(self, data):
        """Дополнительная валидация"""
        if 'user' in data and data['user'] != self.context['request'].user:
            raise serializers.ValidationError({
                "user": "Нельзя изменить владельца транспортного средства"
            })
        return data


class Refueling(serializers.ModelSerializer):
    odometer = serializers.SerializerMethodField(read_only=True)
    fuel_consumption = serializers.SerializerMethodField(read_only=True)
    effective_cost = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=models.Vehicle.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.user and not request.user.is_anonymous:
            self.fields['vehicle'].queryset = models.Vehicle.objects.filter(user=request.user)

    class Meta:
        model = models.Refueling
        fields = '__all__'
        read_only_fields = [
            'odometer', 'month', 'quarter', 'created_at', 'updated_at',
            'total_cost', 'fuel_consumption', 'effective_cost', 'user'
        ]

    def get_odometer(self, obj):
        """Вычисляемое поле одометра"""
        return obj.odometer

    def get_fuel_consumption(self, obj):
        """Расход топлива на 100 км"""
        return obj.fuel_consumption

    def get_effective_cost(self, obj):
        """Стоимость с учетом скидки"""
        return obj.effective_cost

    def validate_vehicle(self, value):
        """Проверяем, что транспортное средство принадлежит пользователю"""
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError(
                "Это транспортное средство не принадлежит вам"
            )
        return value

    def validate(self, data):
        """Валидация последовательности заправок"""
        vehicle = data.get('vehicle')
        date = data.get('date')
        mileage = data.get('mileage')

        if vehicle and date and mileage is not None:
            # Проверяем, что нет заправок с более поздней датой для этого авто
            future_refuels = models.Refueling.objects.filter(
                vehicle=vehicle,
                date__gt=date
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if future_refuels and self.instance is None:
                raise serializers.ValidationError({
                    "date": "Нельзя добавить заправку с датой раньше существующих будущих заправок. "
                            "Сначала удалите или отредактируйте более поздние заправки."
                })

            # Проверяем, что пробег не отрицательный
            if mileage < 0:
                raise serializers.ValidationError({
                    "mileage": "Пробег не может быть отрицательным"
                })

            # Проверка минимального пробега
            if mileage == 0:
                raise serializers.ValidationError({
                    "mileage": "Пробег должен быть больше 0"
                })

            if mileage > 5000:
                raise serializers.ValidationError({
                    "mileage": "Пробег между заправками не может превышать 5000 км"
                })

        return data

    def create(self, validated_data):
        """Создание заправки с автоматическим расчетом total_cost и установкой user"""
        # Убедимся, что total_cost вычислен если не задан
        fuel_quantity = validated_data.get('fuel_quantity')
        price_per_liter = validated_data.get('price_per_liter')
        service_operation = validated_data.get('service_operation', 0)

        if fuel_quantity and price_per_liter and not validated_data.get('total_cost'):
            validated_data['total_cost'] = fuel_quantity * price_per_liter + service_operation

        # Автоматически устанавливаем пользователя
        validated_data['user'] = self.context['request'].user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """При обновлении проверяем права"""
        # Не даем изменить user
        validated_data.pop('user', None)

        # Не даем изменить vehicle на чужой
        if 'vehicle' in validated_data and validated_data['vehicle'].user != self.context['request'].user:
            raise serializers.ValidationError({
                "vehicle": "Нельзя перенести заправку на чужое транспортное средство"
            })

        return super().update(instance, validated_data)


class FuelStatistics(serializers.ModelSerializer):
    class Meta:
        model = models.FuelStatistics
        fields = '__all__'


class GasStation(serializers.ModelSerializer):
    class Meta:
        model = models.GasStation
        fields = '__all__'