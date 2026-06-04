"""
ResNet-50 模型（迁移学习）
使用 ImageNet 预训练权重，微调全连接层
"""
import torch
import torch.nn as nn
from torchvision import models


class ResNet50Classifier(nn.Module):
    """
    ResNet-50 迁移学习分类器:
    - 骨干网络: ResNet-50 (ImageNet 预训练)
    - 分类头: 可配置的全连接层
    """

    def __init__(self, num_classes=102, freeze_backbone=True, dropout=0.3):
        super(ResNet50Classifier, self).__init__()

        # 加载预训练模型
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

        # 冻结骨干网络
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        # 替换分类头
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_features, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)

    def unfreeze_backbone(self):
        """解冻骨干网络用于微调"""
        for param in self.backbone.parameters():
            param.requires_grad = True

    def freeze_backbone(self):
        """冻结骨干网络"""
        for param in self.backbone.parameters():
            param.requires_grad = False


def build_model(num_classes=102, pretrained=True, freeze_backbone=True):
    """构建 ResNet-50 模型"""
    return ResNet50Classifier(
        num_classes=num_classes,
        freeze_backbone=freeze_backbone,
    )
