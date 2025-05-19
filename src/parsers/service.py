from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear
from src.news.models import News

class ParsersService:
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