from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from forge import models


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
