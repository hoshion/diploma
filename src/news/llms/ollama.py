from datetime import datetime

import ollama

from src.news.models import LargeLanguageModel, NewsTranslation, NewsSentiment, Prompt, NewsCluster


class OllamaModel:
    def __init__(self, model_name):
        obj, created = LargeLanguageModel.objects.get_or_create(name=model_name)
        if created:
            obj.save()
        self.model = obj
        self.model_name = model_name

    def get_sentiment(self, parser_type, translator_type, start_year, end_year, start_month, end_month, prompt):
        start_date = datetime(start_year, start_month, 1)
        if end_month == 12:
            end_date = datetime(end_year + 1, 1, 1)
        else:
            end_date = datetime(end_year, end_month + 1, 1)

        translation_items = NewsTranslation.objects.filter(
            news__published_at__gte=start_date,
            news__published_at__lte=end_date,
            news__website__name=parser_type,
            translator__name=translator_type,
        )

        promptDb, created = Prompt.objects.get_or_create(content=prompt)
        if created:
            promptDb.save()

        for translation in translation_items:
            sentimentDb = NewsSentiment.objects.filter(
                translation=translation,
                prompt=promptDb,
                model=self.model,
            )
            if len(sentimentDb) == 0:
                messages = [
                    {"role": "user", "content": promptDb.content + translation.content},
                ]
                response = ollama.chat(model=self.model_name, messages=messages)["message"]["content"]
                if "POSITIVE" in response:
                    value = "POSITIVE"
                elif "NEGATIVE" in response:
                    value = "NEGATIVE"
                elif "NEUTRAL" in response:
                    value = "NEUTRAL"
                else:
                    value = "UNKNOWN"
                sentiment = NewsSentiment(
                    translation=translation,
                    model=self.model,
                    value=value,
                    prompt=promptDb,
                    explanation=response,
                )
                sentiment.save()

    def get_cluster(self, parser_type, translator_type, start_year, end_year, start_month, end_month, prompt):
        start_date = datetime(start_year, start_month, 1)
        if end_month == 12:
            end_date = datetime(end_year + 1, 1, 1)
        else:
            end_date = datetime(end_year, end_month + 1, 1)

        translation_items = NewsTranslation.objects.filter(
            news__published_at__gte=start_date,
            news__published_at__lte=end_date,
            news__website__name=parser_type,
            translator__name=translator_type,
        )

        promptDb, created = Prompt.objects.get_or_create(content=prompt)
        if created:
            promptDb.save()

        for translation in translation_items:
            clusterDb = NewsCluster.objects.filter(
                translation=translation,
                prompt=promptDb,
                model=self.model,
            )
            if len(clusterDb) == 0:
                messages = [
                    {"role": "user", "content": promptDb.content + translation.content},
                ]
                name = ollama.chat(model=self.model_name, messages=messages)["message"]["content"]
                cluster = NewsCluster(
                    translation=translation,
                    model=self.model,
                    name=name,
                    prompt=promptDb,
                )
                cluster.save()