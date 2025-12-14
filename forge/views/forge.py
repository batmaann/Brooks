from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from forge import models


@csrf_exempt
def forge(request):
    if request.method == 'GET':
        qs = models.Refueling.objects.all()

        results = []
        for refueling in qs:
            results.append({
                'id': refueling.id,
                'date': refueling.date,
                'month': refueling.month,
                'quarter': refueling.quarter,
                'mileage': refueling.mileage,
                'odometer': refueling.odometer,
                'fuel_quantity': refueling.fuel_quantity,
                'price_per_liter': refueling.price_per_liter,
                'total_cost': refueling.total_cost,
                'is_full_tank': refueling.is_full_tank,
                'discount': refueling.discount,
                'comment': refueling.comment,
                'fuel_type': refueling.fuel_type,
            })
        return JsonResponse({'results': results})
        # else:
        #     data = request.POST
        #
        #     # Создаем объект Refueling со всеми полями
        #     refueling = models.Refueling(
        #         date=data.get('date'),
        #         month=data.get('month'),
        #         quarter=data.get('quarter'),
        #         mileage=data.get('mileage'),
        #         odometer=data.get('odometer'),
        #         fuel_quantity=data.get('fuel_quantity'),
        #         price_per_liter=data.get('price_per_liter'),
        #         total_cost=data.get('total_cost'),
        #         is_full_tank=data.get('is_full_tank', 'false').lower() == 'true',
        #         discount=data.get('discount', 0),
        #         comment=data.get('comment', ''),
        #         fuel_type=data.get('fuel_type'),
        #     )
        #     refueling.save()
        #     return JsonResponse({'id': refueling.pk}, status=201)