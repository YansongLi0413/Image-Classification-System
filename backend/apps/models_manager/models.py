"""
模型管理模块
"""
from django.db import models


class ModelInfo(models.Model):
    """模型信息"""
    name = models.CharField(max_length=50, verbose_name='模型标识名')
    display_name = models.CharField(max_length=100, verbose_name='显示名称')
    dataset_name = models.CharField(max_length=50, verbose_name='训练数据集')
    accuracy = models.FloatField(default=0, verbose_name='准确率')
    file_path = models.CharField(max_length=500, verbose_name='模型文件路径')
    file_size_mb = models.FloatField(default=0, verbose_name='模型大小(MB)')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'models_info'
        verbose_name = '模型信息'
        verbose_name_plural = '模型信息'
        unique_together = [['name', 'dataset_name']]
