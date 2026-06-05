"""
主路由配置
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import JsonResponse


def health_check(request):
    """健康检查接口"""
    return JsonResponse({'status': 'ok', 'version': '1.0.0'})


urlpatterns = [
    path('', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.predictions.urls')),
    path('api/models/', include('apps.models_manager.urls')),
]
