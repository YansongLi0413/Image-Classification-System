"""
主路由配置
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404
from pathlib import Path


def health_check(request):
    """健康检查接口"""
    return JsonResponse({'status': 'ok', 'version': '1.0.0'})


def serve_storage(request, path):
    """提供 storage 目录下的文件（开发环境用）"""
    file_path = settings.STORAGE_ROOT / path
    if not file_path.exists() or not file_path.is_file():
        raise Http404('文件不存在')
    return FileResponse(open(file_path, 'rb'))


urlpatterns = [
    path('', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.predictions.urls')),
    path('api/models/', include('apps.models_manager.urls')),
    path('storage/<path:path>', serve_storage, name='serve-storage'),
]
