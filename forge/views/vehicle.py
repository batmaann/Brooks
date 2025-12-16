from django.core.serializers import serialize
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from forge import models, serializers
from rest_framework.viewsets import ModelViewSet
from django.views.generic import TemplateView
from forge import filters


# class Status(APIView):
#     def get(self, request):
#         return Response({'status': 'oke'})


class Vehicle(ModelViewSet):
    queryset = models.Vehicle.objects.all()
    serializer_class = serializers.Vehicle
    filterset_class = filters.Vehicle

