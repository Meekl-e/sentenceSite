# Generated by Django 5.1.1 on 2024-11-25 12:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('analysSentenceLogic', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_id', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('date_expired', models.DateTimeField(blank=True)),
                ('sentences', models.ManyToManyField(related_name='sentences_task', to='analysSentenceLogic.sentence')),
                ('students_to', models.ManyToManyField(related_name='students_task', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
