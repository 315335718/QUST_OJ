# Generated by Django 3.1.7 on 2021-03-03 08:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problem', '0002_auto_20210301_1138'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('judge_end_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(-4, 'Submitted'), (-3, 'In queue'), (-2, 'Running'), (-1, 'Wrong answer'), (0, 'Accepted'), (1, 'Time limit exceeded'), (2, 'Idleness limit exceeded'), (3, 'Memory limit exceeded'), (4, 'Runtime error'), (5, 'Denial of judgement'), (6, 'Compilation error'), (7, 'Partial score'), (10, 'Rejected'), (11, 'Checker error'), (12, 'Pretest passed')], db_index=True, default=-4)),
                ('status_percent', models.FloatField(default=0)),
                ('status_detail', models.TextField(blank=True)),
                ('status_time', models.FloatField(blank=True, null=True)),
                ('status_memory', models.FloatField(blank=True, null=True)),
                ('status_message', models.TextField(blank=True)),
                ('status_test', models.PositiveIntegerField(default=0)),
                ('code_length', models.PositiveIntegerField(blank=True, null=True)),
                ('judge_server', models.IntegerField(default=0)),
                ('contest_time', models.DurationField(blank=True, null=True)),
                ('visible', models.BooleanField(db_index=True, default=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problem.problem')),
            ],
            options={
                'verbose_name_plural': '??????????????????',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True)),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='submission.submission')),
            ],
        ),
    ]
