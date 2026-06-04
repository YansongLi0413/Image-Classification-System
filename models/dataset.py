"""
PyTorch Dataset 类 - 加载预处理后的图像数据
"""
import json
import logging
from pathlib import Path

import torch
from torch.utils.data import Dataset
from PIL import Image

logger = logging.getLogger(__name__)


class ImageClassificationDataset(Dataset):
    """
    通用图像分类 Dataset
    从预处理生成的 split_info.json 加载数据
    """

    def __init__(self, split_info_path, split='train', transform=None):
        """
        Args:
            split_info_path: split_info.json 文件路径
            split: 'train', 'val', 'valid', 或 'test'
            transform: torchvision transforms
        """
        self.transform = transform

        # 加载划分信息
        with open(split_info_path, 'r', encoding='utf-8') as f:
            self.split_info = json.load(f)

        # 处理 Oxford 102 的 'valid' → 'val' 兼容
        split_key = split if split in self.split_info['splits'] else \
                    ('valid' if split == 'val' else 'val' if split == 'valid' else split)

        self.samples = self.split_info['splits'][split_key]
        self.num_classes = self.split_info['num_classes']

        logger.info(f"加载 {split} 集: {len(self.samples)} 张图片, {self.num_classes} 个类别")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(sample['path']).convert('RGB')

        if self.transform:
            image = self.transform(image)

        label = sample['class_id']
        return image, label

    def get_class_weights(self):
        """计算类别权重（用于处理类别不平衡）"""
        from collections import Counter
        import numpy as np

        labels = [s['class_id'] for s in self.samples]
        class_counts = Counter(labels)
        total = len(labels)

        weights = []
        for i in range(self.num_classes):
            count = class_counts.get(i, 0)
            weight = total / (self.num_classes * count) if count > 0 else 0.0
            weights.append(weight)

        return torch.tensor(weights, dtype=torch.float32)
