from django.contrib import admin

from comment.models import Article, Comment

admin.site.register(Article)
admin.site.register(Comment)
