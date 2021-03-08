# Generated by Django 3.1.7 on 2021-02-28 17:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=192, verbose_name='题目名称')),
                ('description', models.TextField(blank=True, verbose_name='题目描述')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('checker', models.TextField(blank=True, verbose_name='参考答案')),
                ('table_to_delete', models.TextField(blank=True, verbose_name='要删除的表')),
                ('table_to_do', models.TextField(blank=True, verbose_name='要进行其他操作的表')),
                ('address', models.CharField(blank=True, max_length=192, verbose_name='测试点地址')),
                ('case_total', models.IntegerField(blank=True, default=0, verbose_name='测试点数')),
                ('cases', models.TextField(blank=True, verbose_name='测试点')),
                ('points', models.TextField(blank=True, verbose_name='测试点分数')),
                ('problem_type', models.CharField(choices=[('查询类', '查询类'), ('更新类', '更新类'), ('创建视图类', '创建视图类'), ('创建基本表类', '创建基本表类')], default='查询类', max_length=20, verbose_name='题目类型')),
                ('level', models.CharField(choices=[('简单', '简单'), ('中等', '中等'), ('较难', '较难'), ('困难', '困难')], default='中等', max_length=20, verbose_name='题目难度')),
                ('visible', models.BooleanField(default=True, verbose_name='是否可见')),
                ('ac_user_count', models.PositiveIntegerField(default=0)),
                ('total_user_count', models.PositiveIntegerField(default=0)),
                ('ac_count', models.PositiveIntegerField(default=0)),
                ('total_count', models.PositiveIntegerField(default=0)),
                ('managers', models.ManyToManyField(related_name='managing_problems', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '题目',
                'ordering': ['-pk'],
            },
        ),
    ]
