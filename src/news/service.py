from injector import inject
from datetime import datetime, timedelta
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear
from typing import Optional

from src.news.llms.ollama import OllamaModel
from src.news.models import News, NewsTranslation, NewsSentiment, NewsCluster, NewsWebsite
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

    def delete_news(self, start_date: datetime, end_date: datetime, parser_name: Optional[str] = None) -> int:
        """
        Delete news and related data within a date range
        Args:
            start_date: Start date for deletion range
            end_date: End date for deletion range
            parser_name: Optional name of the parser to filter by
        Returns:
            Number of deleted news items
        """
        # Get all news within the date range
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


class StatisticsService:
    @staticmethod
    def get_parser_statistics(website_id=None, start_date=None, end_date=None, statistic_range='month'):
        """
        Get statistics for parsers within a date range, grouped by specified time range
        """
        query = News.objects.all()
        
        if website_id:
            query = query.filter(website_id=website_id)
        if start_date:
            query = query.filter(published_at__gte=start_date)
        if end_date:
            query = query.filter(published_at__lte=end_date)

        # Choose the appropriate time truncation based on statistic_range
        if statistic_range == 'week':
            trunc_func = TruncWeek('published_at')
        elif statistic_range == 'fortnight':
            # For fortnight, we'll use TruncWeek and then group by 2 weeks
            trunc_func = TruncWeek('published_at')
        elif statistic_range == 'year':
            trunc_func = TruncYear('published_at')
        else:  # default to month
            trunc_func = TruncMonth('published_at')

        # Get statistics grouped by time range
        stats = query.annotate(
            period=trunc_func
        ).values('period', 'website__name').annotate(
            total_parsed=Count('id'),
            total_translated=Count('newstranslation', distinct=True),
            total_sentimented=Count('newstranslation__newssentiment', distinct=True),
            total_clustered=Count('newstranslation__newscluster', distinct=True)
        ).order_by('period')

        # If fortnight is selected, we need to group the weeks into 2-week periods
        if statistic_range == 'fortnight':
            fortnight_stats = []
            current_fortnight = None
            current_stats = None

            for stat in stats:
                period = stat['period']
                # Calculate fortnight number (1-26) for the year
                week_num = period.isocalendar()[1]
                fortnight_num = (week_num - 1) // 2 + 1
                fortnight_start = period - timedelta(days=period.weekday())
                fortnight_end = fortnight_start + timedelta(days=13)
                
                if current_fortnight != fortnight_num:
                    if current_stats:
                        fortnight_stats.append(current_stats)
                    current_fortnight = fortnight_num
                    current_stats = {
                        'period': fortnight_start,
                        'website__name': stat['website__name'],
                        'total_parsed': stat['total_parsed'],
                        'total_translated': stat['total_translated'],
                        'total_sentimented': stat['total_sentimented'],
                        'total_clustered': stat['total_clustered']
                    }
                else:
                    current_stats['total_parsed'] += stat['total_parsed']
                    current_stats['total_translated'] += stat['total_translated']
                    current_stats['total_sentimented'] += stat['total_sentimented']
                    current_stats['total_clustered'] += stat['total_clustered']

            if current_stats:
                fortnight_stats.append(current_stats)
            return list(fortnight_stats)

        return list(stats)