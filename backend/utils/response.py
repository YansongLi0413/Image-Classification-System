"""
统一响应格式 + 自定义异常处理
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """自定义 DRF 异常处理器 — 统一响应格式"""
    response = exception_handler(exc, context)

    if response is not None:
        # 包装错误响应
        response.data = {
            'error': True,
            'code': response.status_code,
            'detail': response.data,
            'path': str(context.get('request', {}).get('path', '')),
        }

    # 未捕获异常
    if response is None:
        logger.error(f"未处理异常: {exc}", exc_info=True)
        return Response({
            'error': True,
            'code': 500,
            'detail': '服务器内部错误',
        }, status=500)

    return response
