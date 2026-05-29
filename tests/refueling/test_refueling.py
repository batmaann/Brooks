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


def test_refueling_creates_expense(api_client, vehicle, user):
    Expense = apps.get_model("expenses", "Expense")
    url = reverse("refueling-list")

    payload = {
        "vehicle": vehicle.id,
        "date": timezone.now().date().isoformat(),
        "mileage": 100,
        "fuel_quantity": "45.50",
        "price_per_liter": "55.30",
        "discount": "10.00",
    }

    response = api_client.post(url, data=payload, format="json")

    assert response.status_code == 201
    expense = Expense.objects.get(source_app="forge", source_model="refueling", source_id=response.data["id"])
    assert expense.user == user
    assert expense.category.slug == "fuel"
    assert expense.amount == Decimal("2506.15")


def test_refueling_updates_and_deletes_expense(api_client, vehicle):
    Expense = apps.get_model("expenses", "Expense")
    url = reverse("refueling-list")
    payload = {
        "vehicle": vehicle.id,
        "date": timezone.now().date().isoformat(),
        "mileage": 100,
        "fuel_quantity": "10.00",
        "price_per_liter": "50.00",
    }
    response = api_client.post(url, data=payload, format="json")
    refueling_id = response.data["id"]

    detail_url = reverse("refueling-detail", kwargs={"pk": refueling_id})
    update_response = api_client.patch(detail_url, data={"price_per_liter": "60.00"}, format="json")

    assert update_response.status_code == 200
    expense = Expense.objects.get(source_app="forge", source_model="refueling", source_id=refueling_id)
    assert expense.amount == Decimal("600.00")

    delete_response = api_client.delete(detail_url)

    assert delete_response.status_code == 204
    assert not Expense.objects.filter(source_app="forge", source_model="refueling", source_id=refueling_id).exists()

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
