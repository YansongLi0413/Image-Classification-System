"""
认证服务 — JWT Token 生成
"""
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthService:
    """用户认证服务"""

    @staticmethod
    def generate_tokens(user) -> dict:
        """为用户生成 JWT token 对"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
