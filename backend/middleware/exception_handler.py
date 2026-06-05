"""
全局异常处理中间件 — 捕获未处理异常并返回 JSON
"""
import logging
import traceback
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware:
    """全局异常处理中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            logger.error(f"未捕获异常 [{request.method}] {request.path}: {e}\n{traceback.format_exc()}")
            return JsonResponse({
                'error': True,
                'code': 500,
                'detail': '服务器内部错误，请稍后重试',
                'path': request.path,
            }, status=500)
