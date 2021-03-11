from django.db import models

from account.models import User


class SchoolClass(models.Model):
    name = models.CharField("班级名", max_length=80, blank=False, unique=True)
    year = models.CharField("学年", max_length=30, choices=(
        ('2020——2021学年', '2020——2021学年'),
        ('2021——2022学年', '2021——2022学年'),
        ('2022——2023学年', '2022——2023学年'),
        ('2023——2024学年', '2023——2024学年'),
        ('2024——2025学年', '2024——2025学年'),
        ('2025——2026学年', '2025——2026学年'),
    ), default='2020——2021学年')
    semester = models.CharField("学期", max_length=20, choices=(
        ('第一学期', '第一学期'),
        ('第二学期', '第二学期'),
    ), default='第二学期')
    student_count = models.PositiveIntegerField("班级人数", default=0)
    tercher = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '班级'

    def __str__(self):
        return self.name
