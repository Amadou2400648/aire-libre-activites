
from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return render(request, "activities/index.html")

def proposer_activite():
    return HttpResponse("Hello, world")

def login_view():
    return HttpResponse("Hello, world")

def signup_view():
    return HttpResponse("Hello, world")

def logout_view():
    return HttpResponse("Hello, world")

def profil():
    return HttpResponse("Hello, world")
