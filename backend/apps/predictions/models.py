"""
预测模块模型 — 图片信息 + 预测记录
"""
from django.db import models
from django.conf import settings


class ImageInfo(models.Model):
    """上传图片信息"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='images', verbose_name='上传用户')
    original_path = models.CharField(max_length=500, verbose_name='原始路径')
    processed_path = models.CharField(max_length=500, blank=True, verbose_name='处理后路径')
    original_size = models.IntegerField(default=0, verbose_name='文件大小(bytes)')
    width = models.IntegerField(default=0, verbose_name='宽度')
    height = models.IntegerField(default=0, verbose_name='高度')
    format = models.CharField(max_length=10, default='jpg', verbose_name='格式')
    image_hash = models.CharField(max_length=64, unique=True, verbose_name='图片哈希')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        db_table = 'predictions_image'
        verbose_name = '图片信息'
        verbose_name_plural = '图片信息'


class PredictionRecord(models.Model):
    """预测记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='predictions', verbose_name='用户')
    image = models.ForeignKey(ImageInfo, on_delete=models.CASCADE,
                              related_name='predictions', verbose_name='关联图片')
    model_name = models.CharField(max_length=50, verbose_name='模型名称')
    dataset_name = models.CharField(max_length=50, verbose_name='数据集名称')
    predicted_class = models.CharField(max_length=200, verbose_name='预测类别')
    predicted_class_id = models.IntegerField(verbose_name='预测类别ID')
    confidence = models.FloatField(verbose_name='置信度')
    top5_results = models.JSONField(default=list, verbose_name='Top-5结果')
    is_correct = models.BooleanField(null=True, blank=True, verbose_name='是否正确')
    inference_time_ms = models.FloatField(default=0, verbose_name='推理耗时(ms)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='预测时间')

    class Meta:
        db_table = 'predictions_record'
        verbose_name = '预测记录'
        verbose_name_plural = '预测记录'
        ordering = ['-created_at']
