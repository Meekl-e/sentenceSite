# Generated by Django 5.0.7 on 2024-09-28 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysSentenceLogic', '0004_remove_sentence_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentence',
            name='data',
            field=models.JSONField(default=dict),
        ),
        migrations.DeleteModel(
            name='Sentence_To_Token',
        ),
        migrations.DeleteModel(
            name='Token',
        ),
    ]