"""
模型管理视图 — 模型列表 + 热更新
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ModelInfo
from services.model_manager import ModelManager

logger = logging.getLogger(__name__)


class ModelListView(APIView):
    """GET /api/models/ — 获取可用模型列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models = ModelInfo.objects.filter(is_active=True)
        data = [{
            'name': m.name,
            'display_name': m.display_name,
            'dataset_name': m.dataset_name,
            'accuracy': m.accuracy,
            'file_size_mb': m.file_size_mb,
        } for m in models]
        return Response({'models': data})


class ModelSwitchView(APIView):
    """POST /api/models/switch/ — 切换默认模型"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        model_name = request.data.get('model')
        if not model_name:
            return Response({'error': '请指定模型名'}, status=400)
        ModelManager.set_default(model_name)
        logger.info(f"默认模型切换为: {model_name}")
        return Response({'message': f'默认模型已切换为 {model_name}', 'model': model_name})


class ModelReloadView(APIView):
    """POST /api/models/reload/ — 模型热更新"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        model_name = request.data.get('model')
        try:
            ModelManager.reload_model(model_name)
            logger.info(f"模型热更新: {model_name}")
            return Response({'message': f'模型 {model_name} 热更新完成'})
        except Exception as e:
            logger.error(f"热更新失败: {e}")
            return Response({'error': str(e)}, status=500)
