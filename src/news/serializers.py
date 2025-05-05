from rest_framework import serializers
from src.news.models import (
    News, NewsSentiment, NewsCategory, NewsTranslation,
    NewsCluster, LargeLanguageModel, Prompt, Translator
)

class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ['id', 'name']

class LargeLanguageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LargeLanguageModel
        fields = ['id', 'name']

class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['id', 'content']

class TranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translator
        fields = ['id', 'name']

class NewsTranslationSerializer(serializers.ModelSerializer):
    translator = TranslatorSerializer(read_only=True)
    
    class Meta:
        model = NewsTranslation
        fields = ['id', 'content', 'translator', 'created_at']

class NewsSentimentSerializer(serializers.ModelSerializer):
    model = LargeLanguageModelSerializer(read_only=True)
    prompt = PromptSerializer(read_only=True)
    
    class Meta:
        model = NewsSentiment
        fields = ['value', 'explanation', 'model', 'prompt', 'created_at']

class NewsClusterSerializer(serializers.ModelSerializer):
    model = LargeLanguageModelSerializer(read_only=True)
    prompt = PromptSerializer(read_only=True)
    
    class Meta:
        model = NewsCluster
        fields = ['name', 'model', 'prompt', 'created_at']

class NewsSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)
    translations = NewsTranslationSerializer(source='newstranslation_set', many=True, read_only=True)
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'published_at', 'category', 'translations']

class NewsDetailSerializer(NewsSerializer):
    translations = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        translations = obj.newstranslation_set.all()
        result = []
        for translation in translations:
            translation_data = NewsTranslationSerializer(translation).data
            translation_data['sentiments'] = NewsSentimentSerializer(
                translation.newssentiment_set.all(), many=True
            ).data
            translation_data['clusters'] = NewsClusterSerializer(
                translation.newscluster_set.all(), many=True
            ).data
            result.append(translation_data)
        return result