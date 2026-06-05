"""
用户视图 — 注册/登录/信息/修改密码
"""
import logging
from django.contrib.auth import update_session_auth_hash
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer, UserInfoSerializer, ChangePasswordSerializer
)
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """POST /api/auth/register/ — 用户注册"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        tokens = AuthService.generate_tokens(user)
        logger.info(f"新用户注册: {user.username}")
        return Response({
            'user': UserInfoSerializer(user).data,
            'tokens': tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/auth/login/ — 用户登录"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': str(serializer.errors)}, status=status.HTTP_401_UNAUTHORIZED)
        user = serializer.validated_data['user']
        tokens = AuthService.generate_tokens(user)
        user.save(update_fields=['last_login'])  # 会被 auto_now 覆盖，手动触发
        logger.info(f"用户登录: {user.username}")
        return Response({
            'user': UserInfoSerializer(user).data,
            'tokens': tokens,
        })


class UserInfoView(APIView):
    """GET /api/auth/me/ — 获取当前用户信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserInfoSerializer(request.user).data)

    def put(self, request):
        serializer = UserInfoSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ — 修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        update_session_auth_hash(request, user)
        logger.info(f"用户修改密码: {user.username}")
        return Response({'message': '密码修改成功'})


class RefreshTokenView(APIView):
    """POST /api/auth/refresh/ — 刷新令牌"""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': '缺少 refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            return Response({
                'access': str(token.access_token),
                'refresh': str(token),
            })
        except Exception:
            return Response({'error': 'Token 无效或已过期'}, status=status.HTTP_401_UNAUTHORIZED)
