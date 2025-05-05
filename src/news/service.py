from injector import inject
from datetime import datetime
from django.db.models import Q

from src.news.llms.ollama import OllamaModel
from src.news.models import News
from src.news.parsers.hromadske import HromadskeParser
from src.news.serializers import NewsDetailSerializer
from src.news.translators.translator import GoogleTranslator


class NewsService:
    def get(self):
        return 'Hello world!'

    def find_many(self, params: dict[str, str]):
        query = Q()
        
        # Add date range filtering if provided
        if 'start_date' in params and 'end_date' in params:
            try:
                start_date = datetime.strptime(params['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(params['end_date'], '%Y-%m-%d')
                query &= Q(published_at__gte=start_date) & Q(published_at__lte=end_date)
            except ValueError:
                pass  # Handle invalid date format silently
        
        objects = News.objects.filter(query)
        return NewsDetailSerializer(objects, many=True)

    def parse(self, params: dict[str, str]):
        if params["parser_type"] == 'Hromadske':
            HromadskeParser(int(params["start_year"]), int(params["end_year"]), int(params["start_month"]), int(params["end_month"])).parse()

    def translate(self, params: dict[str, str]):
        if params["translator_type"] == 'Google':
            GoogleTranslator().translate(params["parser_type"], int(params["start_year"]), int(params["end_year"]), int(params["start_month"]), int(params["end_month"]))

    def sentiment(self, params: dict[str, str]):
        if params["model_type"] == 'llama3.1:8b':
            OllamaModel(params["model_type"]).get_sentiment(
                params["parser_type"],
                params["translator_type"],
                params["start_year"],
                params["end_year"],
                params["start_month"],
                params["end_month"],
                params["prompt"]
            )

    def clusterize(self, params: dict[str, str]):
        if params["model_type"] == 'llama3.1:8b':
            OllamaModel(params["model_type"]).get_cluster(
                params["parser_type"],
                params["translator_type"],
                params["start_year"],
                params["end_year"],
                params["start_month"],
                params["end_month"],
                params["prompt"]
            )