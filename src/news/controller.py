from django.http import HttpResponse, JsonResponse, HttpRequest
import json
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .service import NewsService
from injector import inject
from .serializers import NewsDetailSerializer

class NewsController(viewsets.ViewSet):
    @inject
    def setup(self, request, news_service: NewsService):
        self.news_service = news_service

    def list(self, request: HttpRequest):
        serializer = self.news_service.find_many(request.GET)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def parse(self, request: HttpRequest):
        try:
            self.news_service.parse(request.GET)
            return Response({"message": "success"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['GET'])
    def translate(self, request: HttpRequest):
        try:
            self.news_service.translate(request.GET)
            return Response({"message": "success"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['POST'])
    def sentiment(self, request: HttpRequest):
        try:
            self.news_service.sentiment(json.loads(request.body))
            return Response({"message": "success"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['POST'])
    def clusterize(self, request: HttpRequest):
        try:
            self.news_service.clusterize(json.loads(request.body))
            return Response({"message": "success"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)