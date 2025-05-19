from django.http import HttpResponse, JsonResponse, HttpRequest
import json
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .service import NewsService, StatisticsService
from injector import inject
from .serializers import NewsDetailSerializer
from datetime import datetime
from src.parsers.service import ParsersService

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

    @action(detail=False, methods=['POST'])
    def delete(self, request: HttpRequest):
        try:
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            parser_name = request.data.get('parser_name')

            if not start_date or not end_date:
                return Response({"error": "Start date and end date are required"}, status=400)

            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            deleted_count = self.news_service.delete_news(
                start_date=start_date,
                end_date=end_date,
                parser_name=parser_name
            )

            return Response({
                "message": f"Successfully deleted {deleted_count} news items and related data",
                "deleted_count": deleted_count
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    @action(detail=False, methods=['GET'])
    def statistics(self, request: HttpRequest):
        website_id = request.GET.get('website_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        statistic_range = request.GET.get('statistic_range', 'month')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        statistics = ParsersService.get_parser_statistics(
            website_id=website_id,
            start_date=start_date,
            end_date=end_date,
            statistic_range=statistic_range
        )

        return Response(statistics)