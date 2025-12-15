from django.core.serializers import serialize
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from forge import models, serializers
from rest_framework.viewsets import ModelViewSet
from django.views.generic import TemplateView

@csrf_exempt
def createVehicle(request):
    if request.method == 'POST':
        name = request.POST['name']
        vehicle = models.Vehicle(
            name=name,
            brand=request.POST.get('brand', ''),
            model=request.POST.get('model', ''),
            license_plate=request.POST.get('license_plate', ''),
        )
        vehicle.save()
        return JsonResponse({'id': vehicle.id}, status=201)
    else:
        return JsonResponse({'not okey'}, status=200)


@csrf_exempt
def vehicle(request):
    if request.method == 'GET':
        qs = models.Vehicle.objects.all()
        results = []
        for vehicle in qs:
            results.append({
                'name': vehicle.name,
                'brand': vehicle.brand,
                'model': vehicle.model,
                'license_plate': vehicle.license_plate,

            })
        return JsonResponse({'results': results})


class Status(APIView):
    def get(self, request):

        return Response({'status': 'oke'})

class Vehicle(ModelViewSet):
    queryset = models.Vehicle.objects.all()
    serializer_class = serializers.Vehicle

