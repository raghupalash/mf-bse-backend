from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.views import APIView


# Create your views here.
def hello_world(request):
    return HttpResponse("Hello world!")


class GenerateOTPView(APIView):
    pass
