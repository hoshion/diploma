from django.shortcuts import render
from src.news.models import NewsWebsite

def index(request):
    return render(request, 'index.html')

def settings(request):
    return render(request, 'settings.html')

def statistics_view(request):
    websites = NewsWebsite.objects.all()
    return render(request, 'statistics.html', {'websites': websites })
