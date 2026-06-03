import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework.test import APIClient
import forge.models

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="pass11111111")
    perms = Permission.objects.filter(content_type__app_label='forge', content_type__model='refueling')
    user.user_permissions.set(perms)
    return user


@pytest.fixture
def user2(django_user_model):
    user2 = django_user_model.objects.create_user(username="testuser2", password="pass11111111")
    perms = Permission.objects.filter(content_type__app_label='forge', content_type__model='refueling')
    user2.user_permissions.set(perms)
    return user2


@pytest.fixture
def api_client2(user2):
    client = APIClient()
    client.force_authenticate(user=user2)
    return client


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def vehicle(user):
    return forge.models.Vehicle.objects.create(
        name="Toyota Camry",
        brand="Toyota",
        model="Camry",
        year=2020,
        initial_odometer=1000,
        user=user,
    )


def test_create_vehicle(api_client, user):
    url = reverse("vehicle-list")
    payload = {
        "name": "Toyota Camry"
    }

    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 201
    assert response.data["name"] == payload["name"]
    assert forge.models.Vehicle.objects.count() == 1


def test_access_vehicle(api_client, user, api_client2, user2):
    url = reverse("vehicle-list")
    payload = {"name": "Toyota Camry"}
    response = api_client.post(url, data=payload, format="json")

    assert response.status_code == 201
    created_id = response.data["id"]
    my_cars_response = api_client.get(url, format="json")

    assert my_cars_response.status_code == 200
    car_from_db = forge.models.Vehicle.objects.get(id=created_id)
    assert car_from_db.name == "Toyota Camry"

    other_cars_response = api_client2.get(url, format="json")
    assert other_cars_response.status_code == 200
    assert other_cars_response.data == []


def test_anonymous_user_cannot_access_vehicles(api_client, user, client):
    url = reverse("vehicle-list")
    payload = {
        "name": "Toyota Camry"
    }
    response = api_client.post(url, data=payload, format="json")
    response2 = client.get(url, format="json")
    assert response2.status_code == 401


def test_get_vehicle_by_id(api_client, user, client):
    url_list = reverse("vehicle-list")
    camry_payload = {"name": "Toyota Camry"}
    response_camry = api_client.post(url_list, data=camry_payload, format="json")
    ford_payload = {"name": "Ford Focus"}
    response_ford = api_client.post(url_list, data=ford_payload, format="json")
    ford_id = response_ford.data["id"]
    url_detail = reverse("vehicle-detail", kwargs={"pk": ford_id})
    response_detail = api_client.get(url_detail)
    assert response_detail.data["name"] == "Ford Focus"
    assert forge.models.Vehicle.objects.count() == 2


def test_update_vehicle(api_client, vehicle):
    url = reverse("vehicle-detail", kwargs={"pk": vehicle.id})
    payload = {
        "name": "Toyota Camry Updated",
        "brand": "Toyota",
        "model": "Camry XV70",
        "year": 2021,
        "initial_odometer": 1500,
        "is_active": False,
    }

    response = api_client.patch(url, data=payload, format="json")

    vehicle.refresh_from_db()
    assert response.status_code == 200
    assert response.data["name"] == payload["name"]
    assert response.data["model"] == payload["model"]
    assert vehicle.name == payload["name"]
    assert vehicle.year == payload["year"]
    assert vehicle.initial_odometer == payload["initial_odometer"]
    assert vehicle.is_active is False


def test_update_vehicle_does_not_change_owner(api_client, vehicle, user, user2):
    url = reverse("vehicle-detail", kwargs={"pk": vehicle.id})

    response = api_client.patch(
        url,
        data={
            "name": "Toyota Camry Updated",
            "user": user2.id,
        },
        format="json",
    )

    vehicle.refresh_from_db()
    assert response.status_code == 200
    assert vehicle.user == user
    assert vehicle.name == "Toyota Camry Updated"


def test_delete_vehicle(api_client, vehicle):
    url = reverse("vehicle-detail", kwargs={"pk": vehicle.id})

    response = api_client.delete(url)

    assert response.status_code == 204
    assert forge.models.Vehicle.objects.count() == 0

# #TODO
# # Создание транспорта Done
# # Получение транспорта необходимым пользователем Done
# # отказ в доступе получение чужим пользователем Done
# # отказ в доступе вообще Done
# # получение доступа к транспорту по айди Done
# # Изминение траспорта Done
# # удаление траспорта Done
#
