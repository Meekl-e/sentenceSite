# Generated by Django 5.1.1 on 2024-11-29 12:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('studentTasksLogic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasksentences',
            name='sentence',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]