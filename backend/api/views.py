"""
API views for image classification prediction.
"""
import json
import logging
from pathlib import Path

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class PredictView(APIView):
    """
    POST /api/predict/
    Accepts: { "image": <base64_encoded_image>, "model": "resnet50", "dataset": "caltech101" }
    Returns: { "prediction": "...", "confidence": 0.95, "top5": [...] }
    """

    def post(self, request):
        try:
            image_data = request.data.get('image')
            model_name = request.data.get('model', 'resnet50')
            dataset_name = request.data.get('dataset', 'caltech101')

            if not image_data:
                return Response(
                    {'error': 'No image provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # TODO: Load model and run inference
            # For now, return placeholder
            return Response({
                'prediction': 'Model inference not yet implemented',
                'confidence': 0.0,
                'model': model_name,
                'dataset': dataset_name,
            })

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelListView(APIView):
    """
    GET /api/models/
    Returns list of available models.
    """

    def get(self, request):
        models = [
            {'id': 'custom_cnn', 'name': 'Custom CNN', 'type': 'from_scratch'},
            {'id': 'resnet50', 'name': 'ResNet-50', 'type': 'transfer_learning'},
            {'id': 'efficientnet_b1', 'name': 'EfficientNet-B1', 'type': 'transfer_learning'},
            {'id': 'vit_b16', 'name': 'Vision Transformer (ViT-B/16)', 'type': 'transfer_learning'},
            {'id': 'densenet121', 'name': 'DenseNet-121', 'type': 'transfer_learning'},
        ]
        return Response({'models': models})
