# Generated by Django 5.0.7 on 2024-08-25 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userLogic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='correctuser',
            name='change_sentence',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]