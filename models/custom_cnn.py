"""
自定义 CNN 模型（残差版）
从头训练的卷积神经网络，作为基准对比模型。
相比普通 CNN，加入残差连接和 GAP 分类头，提升训练稳定性和泛化能力。
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    """残差卷积块：Conv3x3 → BN → ReLU → Conv3x3 → BN → +Shortcut → ReLU"""

    def __init__(self, in_channels, out_channels, stride=1):
        super(ResidualBlock, self).__init__()

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3,
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                               stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # 1×1 投影，匹配通道数或空间尺寸
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1,
                          stride=stride, bias=False),
                nn.BatchNorm2d(out_channels),
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)), inplace=True)
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out, inplace=True)
        return out


class CustomCNN(nn.Module):
    """
    自定义残差 CNN 架构:
    - 1 个 Stem 卷积 + 4 个残差块 + GAP 分类头
    - 适用于 224×224 输入，102 类输出
    - 总参数量约 5.5M（比旧版减少 80%）
    """

    def __init__(self, num_classes=102, dropout=0.4):
        super(CustomCNN, self).__init__()

        # Stem: 224 → 112
        self.stem = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
        )

        # 残差阶段 1: 56 → 56, 32 → 64
        self.layer1 = nn.Sequential(
            ResidualBlock(32, 64, stride=1),
            ResidualBlock(64, 64, stride=1),
        )

        # 残差阶段 2: 56 → 28, 64 → 128
        self.layer2 = nn.Sequential(
            ResidualBlock(64, 128, stride=2),
            ResidualBlock(128, 128, stride=1),
        )

        # 残差阶段 3: 28 → 14, 128 → 256
        self.layer3 = nn.Sequential(
            ResidualBlock(128, 256, stride=2),
            ResidualBlock(256, 256, stride=1),
        )

        # 残差阶段 4: 14 → 7, 256 → 512
        self.layer4 = nn.Sequential(
            ResidualBlock(256, 512, stride=2),
            ResidualBlock(512, 512, stride=1),
        )

        # GAP 分类头 — 比旧版 Flatten(25088→1024) 大幅减少参数
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes),
        )

        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out',
                                        nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.stem(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.classifier(x)
        return x


def build_model(num_classes=102, pretrained=False):
    """构建 Custom CNN 模型"""
    return CustomCNN(num_classes=num_classes)
