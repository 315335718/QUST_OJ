# Generated by Django 3.1.7 on 2021-05-25 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0015_auto_20210524_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='visualization',
            field=models.TextField(blank=True, default=None, verbose_name='可视化分析'),
        ),
    ]
