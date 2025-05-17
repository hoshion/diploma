from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.news.controller import NewsController, get_parser_statistics

router = DefaultRouter()
router.register('news', NewsController, basename='news')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/statistics/', get_parser_statistics, name='parser-statistics'),
    path('', include('src.frontend.urls')),
]
