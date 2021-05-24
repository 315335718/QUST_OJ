from django.db import models

from account.models import User


class Article(models.Model):
    description = models.TextField("内容")
    count = models.IntegerField("浏览量", default=0)
    images_count = models.IntegerField("图片数量", default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pk']
        verbose_name_plural = '帖子'

    def __str__(self):
        return '%d. %s' % (self.pk, self.description[:10])


class Comment(models.Model):
    description = models.TextField("评论内容")
    create_time = models.DateTimeField(auto_now_add=True)
    to_comment = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pk']
        verbose_name_plural = '评论'

    def __str__(self):
        return '%d. -> %d' % (self.pk, self.to_comment)
