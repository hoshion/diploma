from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.news.controller import NewsController

router = DefaultRouter()
router.register('news', NewsController, basename='news')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', include('src.frontend.urls')),
]
