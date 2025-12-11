from django.shortcuts import render
from django.http.response import HttpResponse


def utilities(request):
    return HttpResponse('привет жку')