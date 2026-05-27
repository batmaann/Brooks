from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
import users.views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

import forge.views.vehicle
from forge.views.refueling import Refueling
from forge.views.gasStation import GasStation
from forge.views.fuelStatistics import FuelStatistics

router = DefaultRouter()
router.register('vehicle', forge.views.vehicle.Vehicle, basename='vehicle')

router.register('refuelings', Refueling, basename='refueling')
router.register('gasStation', GasStation)
router.register('fuel-statistics', FuelStatistics)


urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/', SpectacularSwaggerView.as_view(url_name='schema')),

    path('user/register/', users.views.RegisterUser.as_view(), name='user_register'),
    path('user/login/', users.views.LoginUser.as_view(), name='user_login'),

]

urlpatterns += router.urls