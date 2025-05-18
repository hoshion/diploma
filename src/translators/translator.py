from datetime import datetime

from deep_translator import GoogleTranslator as DeepGoogleTranslator

from src.news.models import News, Translator, NewsTranslation

class GoogleTranslator:
    translator_name = 'Google'

    def __init__(self):
        obj, created = Translator.objects.get_or_create(name=self.translator_name)
        if created:
            obj.save()
        self.translator = obj

    def translate(self, parser_type, start_year, end_year, start_month, end_month, last_news_date=None):
        start_date = datetime(start_year, start_month, 1)
        if end_month == 12:
            end_date = datetime(end_year + 1, 1, 1)
        else:
            end_date = datetime(end_year, end_month + 1, 1)

        if last_news_date is not None:
            news_items = News.objects.filter(
                published_at__gt=last_news_date,
                website__name=parser_type,
            )
        else:
            news_items = News.objects.filter(
                published_at__gte=start_date,
                published_at__lte=end_date,
                website__name=parser_type,
            )

        for news in news_items:
            en_text = DeepGoogleTranslator(source='auto', target='en').translate(news.content[0:3000])
            newsDb = NewsTranslation.objects.filter(news=news, translator=self.translator)
            if len(newsDb) == 0:
                translation = NewsTranslation(content=en_text, news=news, translator=self.translator)
                translation.save() 