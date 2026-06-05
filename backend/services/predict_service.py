"""
预测服务 — 加载模型 + 执行推理
"""
import json
import logging
import sys
from pathlib import Path

import torch
from torchvision import transforms
from PIL import Image

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models.dataset import ImageClassificationDataset

logger = logging.getLogger(__name__)

# 模型缓存（单例）
_MODEL_CACHE = {}

# 可用模型注册表
AVAILABLE_MODELS = {
    'caltech101': {
        'custom_cnn': 'models.custom_cnn',
        'resnet50': 'models.resnet50',
        'efficientnet_b1': 'models.efficientnet',
        'vit_b16': 'models.vit',
        'densenet121': 'models.densenet',
    },
    'oxford102': {
        'custom_cnn': 'models.custom_cnn',
        'resnet50': 'models.resnet50',
        'efficientnet_b1': 'models.efficientnet',
        'vit_b16': 'models.vit',
        'densenet121': 'models.densenet',
    },
}


class PredictService:
    """预测推理服务"""

    _transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    @classmethod
    def _load_model(cls, model_name: str, dataset_name: str):
        """加载模型（带缓存）"""
        cache_key = f'{model_name}_{dataset_name}'
        if cache_key in _MODEL_CACHE:
            return _MODEL_CACHE[cache_key]

        save_dir = Path(__file__).resolve().parent.parent.parent / 'saved_models'
        ckpt_path = save_dir / f'{model_name}_{dataset_name}_best.pth'

        if not ckpt_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {ckpt_path}")

        # 动态导入模型
        module_path = AVAILABLE_MODELS[dataset_name][model_name]
        module = __import__(module_path, fromlist=['build_model'])
        model = module.build_model(num_classes=102 if dataset_name == 'oxford102' else 101)

        checkpoint = torch.load(ckpt_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)

        _MODEL_CACHE[cache_key] = (model, device)
        logger.info(f"模型已加载: {model_name} on {dataset_name} (device={device})")
        return model, device

    @classmethod
    def predict(cls, image_path: str, model_name: str = 'efficientnet_b1',
                dataset_name: str = 'caltech101') -> dict:
        """对单张图片执行预测"""
        import time

        model, device = cls._load_model(model_name, dataset_name)

        # 加载图片
        img = Image.open(image_path).convert('RGB')
        tensor = cls._transform(img).unsqueeze(0).to(device)

        # 推理
        start = time.perf_counter()
        with torch.no_grad():
            output = model(tensor)
            probs = torch.softmax(output, dim=1)

        # Top-5
        top5_probs, top5_indices = probs.topk(5, dim=1)
        elapsed = (time.perf_counter() - start) * 1000

        top5_results = []
        for i in range(5):
            top5_results.append({
                'class_id': top5_indices[0][i].item(),
                'confidence': round(top5_probs[0][i].item(), 4),
            })

        # 获取类别名
        class_name = cls._get_class_name(dataset_name, top5_indices[0][0].item())

        return {
            'predicted_class': class_name,
            'predicted_class_id': top5_indices[0][0].item(),
            'confidence': round(top5_probs[0][0].item(), 4),
            'top5_results': top5_results,
            'inference_time_ms': round(elapsed, 2),
        }

    @classmethod
    def _get_class_name(cls, dataset_name: str, class_id: int) -> str:
        """获取类别名"""
        processed_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'processed'
        split_file = processed_dir / dataset_name / 'split_info.json'

        try:
            with open(split_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            idx_to_class = info.get('idx_to_class', {})
            return idx_to_class.get(str(class_id), f'class_{class_id}')
        except Exception:
            return f'class_{class_id}'

    @classmethod
    def reload_model(cls, model_name: str, dataset_name: str = None):
        """热更新：清除缓存并重新加载"""
        if dataset_name:
            cache_key = f'{model_name}_{dataset_name}'
            _MODEL_CACHE.pop(cache_key, None)
            cls._load_model(model_name, dataset_name)
        else:
            # 清除所有包含该模型名的缓存
            keys_to_remove = [k for k in _MODEL_CACHE if model_name in k]
            for k in keys_to_remove:
                _MODEL_CACHE.pop(k, None)
        logger.info(f"模型热更新完成: {model_name}")
