from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

import forge.views.vehicle
from forge.views.refueling import Refueling
from forge.views.fuelStatistics import FuelStatistics

router = DefaultRouter()
router.register('vehicle', forge.views.vehicle.Vehicle)
router.register('refuelings', Refueling)
#router.register('fuelStatistics', FuelStatistics)


urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/', SpectacularSwaggerView.as_view(url_name='schema')),

    # path('status/', forge.views.vehicle.Status.as_view()),
]

urlpatterns += router.urls