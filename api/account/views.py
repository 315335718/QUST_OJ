from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from account.models import User


class GetMyInfoView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        user_id = request.GET.get('user_id', 0)
        if int(user_id) == 0:
            return Response({'flag': 0, 'message': '检查是否登录或网络连接是否正常'})  # 检查是否未登录
        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            return Response({'flag': 0, 'message': '系统错误: ' + str(str(e).encode())})
        return Response({'flag': 1, 'name': user.name, 'email': user.email})


class UpdateMyInfoView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user_id = request.POST.get('user_id', 0)
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        if int(user_id) == 0:
            return Response({'flag': 0, 'message': '检查是否登录或网络连接是否正常'})  # 检查是否未登录
        try:
            user = User.objects.get(pk=user_id)
            if name != '':
                user.name = name
            if email != '':
                cur = User.objects.filter(email=email)
                if len(cur) == 0:
                    user.email = email
                elif len(cur) > 0 and cur[0].id != int(user_id):
                    return Response({'flag': 0, 'message': '该邮箱已存在'})
            user.save(update_fields=['name', 'email'])
        except Exception as e:
            return Response({'flag': 0, 'message': '系统错误: ' + str(str(e).encode())})
        return Response({'flag': 1, 'message': '更新成功'})