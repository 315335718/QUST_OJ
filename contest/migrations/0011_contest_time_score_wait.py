# Generated by Django 3.1.7 on 2021-04-14 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0010_auto_20210314_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='time_score_wait',
            field=models.IntegerField(default=20, verbose_name='多长时间后分数衰减'),
        ),
    ]
