"""
预测视图 — 上传图片 + 预测 + 历史记录
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ImageInfo, PredictionRecord
from .serializers import (
    PredictRequestSerializer, PredictionRecordSerializer, ImageInfoSerializer
)
from services.predict_service import PredictService
from services.image_service import ImageService
from utils.validators import validate_image
from utils.cache import cache_get, cache_set, CACHE_TTL

logger = logging.getLogger(__name__)


class PredictView(APIView):
    """POST /api/predict/ — 上传图片并预测"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 校验图片
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': '请上传图片'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, err_msg = validate_image(image_file)
        if not is_valid:
            return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)

        model_name = request.data.get('model', 'efficientnet_b1')
        dataset_name = request.data.get('dataset', 'caltech101')

        try:
            # 保存图片
            image_info = ImageService.save_image(image_file, request.user)

            # 检查缓存
            cache_key = f'predict:{image_info.image_hash}:{model_name}'
            cached = cache_get(cache_key)
            if cached:
                cached['from_cache'] = True
                return Response(cached)

            # 执行预测
            result = PredictService.predict(
                image_path=image_info.original_path,
                model_name=model_name,
                dataset_name=dataset_name,
            )

            # 保存预测记录
            record = PredictionRecord.objects.create(
                user=request.user,
                image=image_info,
                model_name=model_name,
                dataset_name=dataset_name,
                predicted_class=result['predicted_class'],
                predicted_class_id=result['predicted_class_id'],
                confidence=result['confidence'],
                top5_results=result['top5_results'],
                inference_time_ms=result['inference_time_ms'],
            )

            response_data = {
                'record_id': record.id,
                'predicted_class': result['predicted_class'],
                'predicted_class_id': result['predicted_class_id'],
                'confidence': result['confidence'],
                'top5_results': result['top5_results'],
                'inference_time_ms': result['inference_time_ms'],
                'image_url': f'/storage/images/original/{image_info.original_path.split(chr(92))[-1]}',
                'from_cache': False,
            }

            # 缓存结果
            cache_set(cache_key, response_data, CACHE_TTL['prediction'])

            logger.info(f"预测完成: user={request.user.username}, model={model_name}, "
                        f"result={result['predicted_class']}, conf={result['confidence']:.3f}")
            return Response(response_data)

        except Exception as e:
            logger.error(f"预测失败: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HistoryView(APIView):
    """GET /api/history/ — 获取预测历史"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        model_filter = request.query_params.get('model', '')

        queryset = PredictionRecord.objects.filter(user=request.user)
        if model_filter:
            queryset = queryset.filter(model_name=model_filter)

        total = queryset.count()
        records = queryset[(page - 1) * page_size: page * page_size]

        return Response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'records': PredictionRecordSerializer(records, many=True).data,
        })


class HistoryDetailView(APIView):
    """GET /api/history/<id>/ — 预测详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            record = PredictionRecord.objects.get(id=pk, user=request.user)
            return Response(PredictionRecordSerializer(record).data)
        except PredictionRecord.DoesNotExist:
            return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)


class HotRecordsView(APIView):
    """GET /api/history/hot/ — 热门预测（Top-N）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Count
        hot = PredictionRecord.objects.values('predicted_class') \
            .annotate(count=Count('id')).order_by('-count')[:10]
        return Response({'hot_predictions': list(hot)})
