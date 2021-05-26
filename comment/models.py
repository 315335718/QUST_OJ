from django.db import models

from account.models import User


class Article(models.Model):
    description = models.TextField("内容",max_length =2000)
    count = models.IntegerField("浏览量",default=0)
    comment_count = models.IntegerField("评论量", default=0)
    images_count = models.IntegerField("图片数量", default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    to_comment = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True)
    to_small_comment = models.IntegerField('面向小评论', default=0)
    description = models.TextField("评论内容",max_length =148)
    create_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)