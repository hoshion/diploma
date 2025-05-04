from django.db import models

class NewsCategory(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class NewsWebsite(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class News(models.Model):
    title = models.CharField(max_length=200, null=True)
    content = models.TextField()
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)
    website = models.ForeignKey(NewsWebsite, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class Prompt(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class LargeLanguageModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class Translator(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class NewsTranslation(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    translator=models.ForeignKey(Translator, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class NewsSentiment(models.Model):
    translation = models.ForeignKey(NewsTranslation, on_delete=models.CASCADE)
    model=models.ForeignKey(LargeLanguageModel, on_delete=models.CASCADE)
    prompt=models.ForeignKey(Prompt, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class NewsCluster(models.Model):
    translation = models.ForeignKey(NewsTranslation, on_delete=models.CASCADE)
    model = models.ForeignKey(LargeLanguageModel, on_delete=models.CASCADE)
    prompt=models.ForeignKey(Prompt, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
