from django.shortcuts import render
from django.http.response import HttpResponse
# Create your views here.

def forge(request):
    return render(request,'forge/forge.html')