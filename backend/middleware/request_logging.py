"""
请求日志中间件 — 记录所有 API 请求
"""
import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """记录每个 HTTP 请求的 method/path/status/duration"""

    def __init__(self, get_response):
        self.get_response = get_response
        # 排除的路径前缀
        self.skip_prefixes = ['/admin/', '/static/', '/storage/']

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = (time.time() - start) * 1000

        path = request.path
        if not any(path.startswith(p) for p in self.skip_prefixes):
            logger.info(
                f"[{request.method}] {path} → {response.status_code} ({duration:.1f}ms)"
            )

        return response
