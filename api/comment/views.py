from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.views import View
# from django.http import HttpResponse

from account.models import User
from comment.models import Article
from comment.models import Comment
from problem.models import Problem
from submission.models import Submission


class creat_articalView(APIView):
    def post(self, request):
        text = request.POST.get('text', 1)
        userid = request.POST.get('user_id',1)
        images_count = int(request.POST.get('images_count',1))
        article = Article.objects.create(author_id=userid,description=text,images_count=images_count)
        id = article.id
        return Response({"status": True,"id":id})


class UserSerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'wx_avatar_url')


class articalSerializer(serializers.ModelSerializer):
    author = UserSerSerializer()
    class Meta:
        model = Article
        fields = ( "description","images_count","count","update_time","author","id","comment_count")


class list_articalView(APIView):
    def get(self, request):
        length = int(request.GET.get('length', 0))
        alist = Article.objects.all().select_related('author').only('author__id', 'author__wx_avatar_url')
        alist = alist.order_by("-update_time")
        alist = alist[length: length+5]
        serializer = articalSerializer(alist, many=True)
        return Response(serializer.data)


class artical_listCountView(APIView):
    def post(self, request):
        id = int(request.POST.get('id', 1))
        article = Article.objects.get(id=id)
        Article.objects.filter(id=id).update(count = article.count+1)
        return Response({"status": True,"count":article.count+1})


class search_articaltView(APIView):
    def post(self, request):
        text = request.POST.get('text', 1)
        alist = Article.objects.filter(description__icontains=text)
        alist = alist.order_by("-count", "-update_time")
        serializer = articalSerializer(alist, many=True)
        return Response(serializer.data)


class artical_detailView(APIView):
    def get(self, request):
        id = int(request.GET.get('id', 1))
        alist = Article.objects.filter(id=id).select_related('author').only('author_id', 'author__wx_avatar_url')
        serializer = articalSerializer(alist, many=True)
        return Response(serializer.data)


class comment_creatView(APIView):
    def post(self, request):
        text = request.POST.get('text', 1)
        userid = int(request.POST.get('user_id',1))
        to_comment = request.POST.get('to_comment',None)
        to_small_comment = int(request.POST.get('to_small_comment',0))
        artical_id =request.POST.get('artical_id',0)
        comment = Comment.objects.create(author_id=userid,description=text, article_id=artical_id,to_comment_id=to_comment,to_small_comment=to_small_comment)
        article = Article.objects.get(id=artical_id)
        Article.objects.filter(id=artical_id).update(comment_count=article.comment_count + 1)
        id = comment.id
        return Response({"status": True,"id":id})


class UserSerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'wx_avatar_url')


class SCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ( "description","create_time","author","id","to_comment")


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerSerializer()
    # to_comment = SCommentSerializer()
    class Meta:
        model = Comment
        fields = ( "description","create_time","author","id","to_comment")


class comment_listView(APIView):
    def get(self, request):
        artical_i = request.GET.get('artical_id')
        artical_id = request.GET.get('artical_id', 1)
        article = Article.objects.get(id=artical_id)
        comments = article.comment_set.all().select_related('author', 'to_comment')
        res = dict()
        for it in comments:
            if it.to_comment == None:
                one = ['一级评论', it.id, it.description, it.create_time, {'user_id': it.author.id, 'username': it.author.\
                    username, 'url': it.author.wx_avatar_url}]
                res[it.id] = [one]
            else:
                one = [it.id, it.description, it.create_time, {'user_id': it.author.id, 'username': it.author.\
                    username, 'url': it.author.wx_avatar_url}, {'user_id': it.to_comment.author.id, 'username': it.to_comment.\
                    author.username, 'url': it.to_comment.author.wx_avatar_url}]
                if it.to_small_comment == 0:
                    one.append(2)
                    res[it.to_comment.id].append(one)
                else:
                    one.append(3)
                    res[it.to_small_comment].append(one)
        return Response({'comments': res})