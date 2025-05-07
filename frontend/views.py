from django.shortcuts import render
from src.news.models import NewsWebsite

# Create your views here.

def index(request):
    return render(request, 'frontend/index.html')

def settings(request):
    return render(request, 'frontend/settings.html')

def statistics_view(request):
    websites = NewsWebsite.objects.all()
    return render(request, 'statistics.html', {'websites': websites})
