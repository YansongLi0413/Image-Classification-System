"""
Vision Transformer (ViT-B/16) 模型（迁移学习）
使用 ImageNet-21k + ImageNet-1k 预训练权重
"""
import torch
import torch.nn as nn
from torchvision import models


class ViTClassifier(nn.Module):
    """
    Vision Transformer (ViT-B/16) 分类器:
    - 骨干网络: ViT-B/16 (ImageNet-21k 预训练 → ImageNet-1k 微调)
    - 分类头: 替换为任务适配的线性层
    """

    def __init__(self, num_classes=102, freeze_backbone=True, dropout=0.2):
        super(ViTClassifier, self).__init__()

        # 加载预训练 ViT (IMAGENET1K_V1 使用 224x224 输入)
        self.backbone = models.vit_b_16(
            weights=models.ViT_B_16_Weights.IMAGENET1K_V1
        )

        # 冻结骨干网络
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        # 替换分类头
        in_features = self.backbone.heads.head.in_features
        self.backbone.heads.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)

    def unfreeze_backbone(self):
        """解冻骨干网络"""
        for param in self.backbone.parameters():
            param.requires_grad = True

    def freeze_backbone(self):
        """冻结骨干网络"""
        for param in self.backbone.parameters():
            param.requires_grad = False


def build_model(num_classes=102, pretrained=True, freeze_backbone=True):
    """构建 ViT-B/16 模型"""
    return ViTClassifier(
        num_classes=num_classes,
        freeze_backbone=freeze_backbone,
    )
