"""
预测序列化器
"""
from rest_framework import serializers
from .models import ImageInfo, PredictionRecord


class ImageInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageInfo
        fields = ['id', 'original_path', 'width', 'height', 'format',
                  'original_size', 'uploaded_at']


class PredictionRecordSerializer(serializers.ModelSerializer):
    image = ImageInfoSerializer(read_only=True)

    class Meta:
        model = PredictionRecord
        fields = ['id', 'image', 'model_name', 'dataset_name',
                  'predicted_class', 'predicted_class_id', 'confidence',
                  'top5_results', 'is_correct', 'inference_time_ms', 'created_at']


class PredictRequestSerializer(serializers.Serializer):
    """预测请求参数"""
    image = serializers.ImageField()
    model = serializers.CharField(default='efficientnet_b1')
    dataset = serializers.CharField(default='caltech101')
