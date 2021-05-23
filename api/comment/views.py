from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from account.models import User
from comment.models import Article


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
        fields = ('id', 'username', 'email')


class articalSerializer(serializers.ModelSerializer):
    author = UserSerSerializer()
    class Meta:
        model = Article
        fields = ( "description","images_count","count","update_time","author")


class list_articalView(APIView):
    def get(self, request):
        alist = Article.objects.all().select_related('author').only('author_id', 'author__email')
        serializer = articalSerializer(alist, many=True)
        return Response(serializer.data)