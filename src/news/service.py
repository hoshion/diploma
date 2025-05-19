from datetime import datetime
from django.db.models import Q
from typing import Optional

from src.llms.ollama import OllamaModel
from src.news.models import News, NewsTranslation, NewsSentiment, NewsCluster
from src.parsers.hromadske import HromadskeParser
from src.news.serializers import NewsDetailSerializer
from src.translators.translator import GoogleTranslator


class NewsService:
    # Метод для отримання новин в базі даних
    def find_many(self, params: dict[str, str]):
        # Створення об'єкту класу для фільтрації
        query = Q()
        
        # Формування фільтрів початкової та кінцевої дати
        if 'start_date' in params and 'end_date' in params:
            try:
                # Отримання значень дат у відповідному форматі
                start_date = datetime.strptime(params['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(params['end_date'], '%Y-%m-%d')
                query &= Q(published_at__gte=start_date) & Q(published_at__lte=end_date)
            except ValueError:
                pass  # Пропустити фільтрацію у випадку помилки
        
        # Отримання об'єктів новин з фільтром
        objects = News.objects.filter(query)

        # Серіалізування новин для відповіді
        return NewsDetailSerializer(objects, many=True)

    # Метод для виклику класу відповідного парсеру з передачею необхідних параметрів
    def parse(self, params: dict[str, str]):
        if params["parser_type"] == 'Hromadske':
            HromadskeParser(int(params["start_year"]), int(params["end_year"]), int(params["start_month"]), int(params["end_month"])).parse()

    # Метод для виклику класу відповідного перекладача з передачею необхідних параметрів
    def translate(self, params: dict[str, str]):
        if params["translator_type"] == 'Google':
            GoogleTranslator().translate(
                params["parser_type"],
                int(params["start_year"]),
                int(params["end_year"]),
                int(params["start_month"]),
                int(params["end_month"])
            )

    # Метод для виклику методу визначення тональності 
    # відповідної великої мовної моделі з передачею необхідних параметрів
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

    # Метод для виклику методу кластеризації 
    # відповідної великої мовної моделі з передачею необхідних параметрів
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

    # Метод для видалення новин з бази даних
    def delete_news(self, start_date: datetime, end_date: datetime, parser_name: Optional[str] = None) -> int:
        # Отримання новин
        news_query = News.objects.filter(published_at__gte=start_date, published_at__lte=end_date)
        if parser_name:
            news_query = news_query.filter(website__name=parser_name)

        # Get all translations for these news
        translations = NewsTranslation.objects.filter(news__in=news_query)
        
        # Delete sentiments and clusters first (they depend on translations)
        NewsSentiment.objects.filter(translation__in=translations).delete()
        NewsCluster.objects.filter(translation__in=translations).delete()
        
        # Delete translations
        translations.delete()
        
        # Finally delete the news
        deleted_count = news_query.delete()[0]
        
        return deleted_count