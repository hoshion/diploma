from celery import shared_task
from datetime import datetime
from src.parsers.hromadske import HromadskeParser
from src.translators.translator import GoogleTranslator
from src.llms.ollama import OllamaModel
from src.news.models import News
from src.news.serializers import NewsDetailSerializer

@shared_task()
def hromadske_news_pipeline():
    print("[Scheduler] Starting Hromadske news pipeline for today.")
    try:
        # Get the last news date directly from the model instance
        last_news = News.objects.order_by('-published_at').first()
        last_news_date = last_news.published_at if last_news else None
        
        today = datetime.now().date()
        start_year = today.year
        end_year = today.year
        start_month = today.month
        end_month = today.month
        days = [today.day]
        parser_type = 'Hromadske'
        translator_type = 'Google'
        model_type = 'llama3.1:8b'
        prompt = """Hi! I need you to analyze sentimentally Ukrainian news. There are three types: POSITIVE, NEGATIVE or NEUTRAL. You need to evaluate the impact of described situation for Ukraine (is it good for Ukrainian or not) and mark as one of three types. As answer you need to write POSITIVE, NEGATIVE or NEUTRAL and short explanation of your decision.

    The news is:
    """
        promptCluster = """Hi! I need you to classify Ukrainian news by news category. There are 17 categories: Economics, Politics, Social, War, World, Religion, Education, Science, Sport, Culture, Useful, Showbiz, Lifestyle, Health, Weather, Other. You need to evaluate the closest category from proposed to this news. As answer you need to write only the name of cateogory and NOTHING ELSE.\n\nThe news is:\n"""

        # 1. Parse only today's news
        print("[Scheduler] Parsing news...")
        parser = HromadskeParser(start_year, end_year, start_month, end_month, days=days)
        parser.parse()
        print("[Scheduler] Parsing complete.")

        # 2. Translate only today's news
        print("[Scheduler] Translating news...")
        translator = GoogleTranslator()
        translator.translate(parser_type, start_year, end_year, start_month, end_month, last_news_date)
        print("[Scheduler] Translation complete.")

        # 3. Analyze sentiment for today's news
        print("[Scheduler] Analyzing sentiment...")
        model = OllamaModel(model_type)
        model.get_sentiment(parser_type, translator_type, start_year, end_year, start_month, end_month, prompt, last_news_date)
        print("[Scheduler] Sentiment analysis complete.")

        # 4. Cluster today's news
        print("[Scheduler] Clustering news...")
        model.get_cluster(parser_type, translator_type, start_year, end_year, start_month, end_month, promptCluster, last_news_date)
        print("[Scheduler] Clustering complete.")
        print("[Scheduler] Hromadske news pipeline finished for today.")
        return True
    except Exception as e:
        print(f"[Scheduler] Error in Hromadske news pipeline: {e}")
        return False
