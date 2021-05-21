from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from account.models import User
from comment.models import Article


class creat_articalView(APIView):
    def post(self, request):
        title = request.POST.get('title',1)
        des = request.POST.get('html',1)
        text = request.POST.get('text', 1)
        userid = request.POST.get('user_id',1)
        Article.objects.create(title=title,description=des,author_id=userid,description_text=text)
        return Response({"status": True})


class UserSerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class articalSerializer(serializers.ModelSerializer):
    author = UserSerSerializer()

    class Meta:
        model = Article
        fields = ("title", "description","description_text","count","update_time","author")


class list_articalView(APIView):
    def get(self, request):
        alist = Article.objects.all().select_related('author').only('author_id', 'author__email')
        serializer = articalSerializer(alist, many=True)
        return Response(serializer.data)