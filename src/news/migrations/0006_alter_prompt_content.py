# Generated by Django 5.2 on 2025-05-03 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_largelanguagemodel_prompt_newssentiment_newscluster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prompt',
            name='content',
            field=models.TextField(),
        ),
    ]
