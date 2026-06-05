"""
模型管理服务 — 热更新 + 默认模型切换
"""
import logging
from services.predict_service import PredictService

logger = logging.getLogger(__name__)

# 默认模型配置
DEFAULT_MODEL = 'efficientnet_b1'
DEFAULT_DATASET = 'caltech101'


class ModelManager:
    """模型生命周期管理"""

    _current_model = DEFAULT_MODEL
    _current_dataset = DEFAULT_DATASET

    @classmethod
    def get_default(cls) -> tuple:
        """获取当前默认模型和数据集"""
        return cls._current_model, cls._current_dataset

    @classmethod
    def set_default(cls, model_name: str, dataset_name: str = None):
        """切换默认模型"""
        cls._current_model = model_name
        if dataset_name:
            cls._current_dataset = dataset_name
        # 预加载新默认模型
        try:
            PredictService._load_model(model_name, cls._current_dataset)
        except Exception as e:
            logger.warning(f"预加载模型失败: {e}")

    @classmethod
    def reload_model(cls, model_name: str = None):
        """热更新指定的模型"""
        target = model_name or cls._current_model
        PredictService.reload_model(target)
        logger.info(f"模型 {target} 已重新加载")

    @classmethod
    def preload_models(cls):
        """启动时预加载默认模型"""
        try:
            PredictService._load_model(cls._current_model, cls._current_dataset)
            logger.info(f"默认模型预加载完成: {cls._current_model}")
        except Exception as e:
            logger.warning(f"预加载默认模型失败: {e}")
