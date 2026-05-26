from decimal import Decimal

import pytest
from django.apps import apps
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="pass11111111")
    perms = Permission.objects.filter(content_type__app_label='forge', content_type__model='refueling')
    user.user_permissions.set(perms)
    return user


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def vehicle(user):
    Vehicle = apps.get_model("forge", "Vehicle")
    return Vehicle.objects.create(
        name="Тестовый автомобиль (Toyota Camry)",
        user=user,
    )


# @pytest.fixture
# def refueling(user, vehicle):
#     Refueling = apps.get_model("forge", "Refueling")
#
#     return Refueling.objects.create(
#         vehicle=vehicle,
#         date=timezone.now().date(),
#         mileage=100,
#         fuel_quantity=Decimal("45.5"),
#         price_per_liter=Decimal("55.30"),
#         user=user,
#     )


def test_create_refueling(api_client, vehicle, user):
    url = reverse("refueling-list")

    payload = {
        "vehicle": vehicle.id,
        "date": timezone.now().date().isoformat(),
        "mileage": 100,
        "fuel_quantity": "45.50",
        "price_per_liter": "55.30",
    }

    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 201
    assert isinstance(response.data, dict)
    assert "id" in response.data

# TODO
# Автоподстановка пользователя (user):
# Проверить, что если user не указан при сохранении,
# он автоматически берется из связанного автомобиля (vehicle.user).
#
# Обновление одометра автомобиля (vehicle.current_odometer)
# роверить, что после сохранения заправки current_odometer
# у связанного Vehicle увеличивается на сумму initial_odometer + все mileage
#
#
#
# Тесты для вычисляемого свойства
# Проверить, что для второй и следующих заправок odometer корректно
# суммирует одометр предыдущей заправки и mileage текущей.
#
#
#
# Тесты валидации данных (Validation & Constraints)
# Отрицательные значения:Убедиться, что MinValueValidator(0) выбрасывает
# ValidationError при попытке сохранить отрицательные значения в поля: mileage, fuel_quantity,
# price_per_liter, total_cost, discount.
#
#
#
#
# Тесты связей и метаданных
# Удаление связанных объектов (on_delete):
# Проверить on_delete=models.CASCADE для vehicle: при удалении машины должны удаляться и её заправки.
#
# Проверить on_delete=models.SET_NULL для gas_station: при удалении АЗС запись заправки должна остаться, но поле gas_station должно стать None.
#
#
#
#
#
#
