from django.db import models

from account.models import User


class Article(models.Model):
    title = models.CharField("名称", max_length=192)
    description = models.TextField("内容")
    description_text = models.TextField("text", default=None)
    count = models.IntegerField("浏览量", default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    description = models.TextField("评论内容")
    create_time = models.DateTimeField(auto_now_add=True)
    to_comment = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
