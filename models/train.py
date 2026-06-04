"""
模型训练入口脚本
用法:
    python models/train.py --model resnet50 --dataset caltech101
    python models/train.py --model custom_cnn --dataset oxford102
    python models/train.py --model all --dataset all
"""
import argparse
import logging
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.dataset import ImageClassificationDataset
from models.trainer import Trainer

# 模型构建函数
from models.custom_cnn import build_model as build_custom_cnn
from models.resnet50 import build_model as build_resnet50
from models.efficientnet import build_model as build_efficientnet
from models.vit import build_model as build_vit
from models.densenet import build_model as build_densenet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT_DIR / 'data' / 'processed'
SAVE_DIR = ROOT_DIR / 'saved_models'

# 模型注册表
MODEL_BUILDERS = {
    'custom_cnn': build_custom_cnn,
    'resnet50': build_resnet50,
    'efficientnet_b1': build_efficientnet,
    'vit_b16': build_vit,
    'densenet121': build_densenet,
}

# 数据集配置
DATASET_CONFIGS = {
    'caltech101': {
        'split_file': PROCESSED_DIR / 'caltech101' / 'split_info.json',
    },
    'oxford102': {
        'split_file': PROCESSED_DIR / 'oxford102' / 'split_info.json',
    },
}


def get_transforms(dataset_name, is_train=True):
    """获取数据增强/预处理 transforms"""
    if is_train:
        return transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])


def get_dataloaders(dataset_name, batch_size=32, num_workers=2):
    """创建数据加载器"""
    config = DATASET_CONFIGS[dataset_name]
    split_file = config['split_file']

    if not split_file.exists():
        raise FileNotFoundError(
            f"划分文件不存在: {split_file}\n"
            f"请先运行: python scripts/preprocess.py"
        )

    train_dataset = ImageClassificationDataset(
        split_file, split='train',
        transform=get_transforms(dataset_name, is_train=True),
    )

    val_split = 'val' if dataset_name == 'caltech101' else 'valid'
    val_dataset = ImageClassificationDataset(
        split_file, split=val_split,
        transform=get_transforms(dataset_name, is_train=False),
    )

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True,
    )

    return train_loader, val_loader, train_dataset.num_classes


def train_model(model_name, dataset_name, epochs=50, batch_size=32,
                lr=0.001, freeze_backbone=True, num_workers=2):
    """训练单个模型"""

    # 获取设备
    if torch.cuda.is_available():
        device = torch.device('cuda')
        logger.info(f"使用 GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        logger.info("使用 CPU")

    # 获取数据
    train_loader, val_loader, num_classes = get_dataloaders(
        dataset_name, batch_size, num_workers
    )

    # 构建模型
    build_fn = MODEL_BUILDERS[model_name]
    if model_name == 'custom_cnn':
        model = build_fn(num_classes=num_classes)
    else:
        model = build_fn(num_classes=num_classes, freeze_backbone=freeze_backbone)

    model = model.to(device)

    # 计算参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"总参数: {total_params:,}")
    logger.info(f"可训练参数: {trainable_params:,}")

    # 训练
    trainer = Trainer(
        model=model, device=device,
        save_dir=SAVE_DIR,
        model_name=model_name,
        dataset_name=dataset_name,
    )

    trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=epochs,
        lr=lr,
        weight_decay=1e-4,
        scheduler_patience=5,
        early_stop_patience=10,
    )

    # 保存训练历史
    trainer.save_history()

    return trainer.best_acc


def main():
    parser = argparse.ArgumentParser(description='训练图像分类模型')
    parser.add_argument('--model', type=str, default='resnet50',
                        choices=['all', 'custom_cnn', 'resnet50', 'efficientnet_b1',
                                 'vit_b16', 'densenet121'],
                        help='模型名称 (default: resnet50)')
    parser.add_argument('--dataset', type=str, default='caltech101',
                        choices=['all', 'caltech101', 'oxford102'],
                        help='数据集名称 (default: caltech101)')
    parser.add_argument('--epochs', type=int, default=50, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=32, help='批次大小')
    parser.add_argument('--lr', type=float, default=0.001, help='学习率')
    parser.add_argument('--freeze_backbone', action='store_true', default=True,
                        help='冻结骨干网络 (迁移学习)')
    parser.add_argument('--unfreeze', action='store_true',
                        help='解冻骨干网络')
    parser.add_argument('--num_workers', type=int, default=2, help='数据加载线程数')

    args = parser.parse_args()

    # 处理 unfreeze
    freeze = not args.unfreeze if args.unfreeze else args.freeze_backbone

    # 确定要训练的模型和数据集
    models_to_train = list(MODEL_BUILDERS.keys()) if args.model == 'all' else [args.model]
    datasets_to_train = list(DATASET_CONFIGS.keys()) if args.dataset == 'all' else [args.dataset]

    results = {}

    for dataset_name in datasets_to_train:
        for model_name in models_to_train:
            logger.info(f"\n{'='*60}")
            logger.info(f"训练: {model_name} on {dataset_name}")
            logger.info(f"{'='*60}\n")

            try:
                acc = train_model(
                    model_name=model_name,
                    dataset_name=dataset_name,
                    epochs=args.epochs,
                    batch_size=args.batch_size,
                    lr=args.lr,
                    freeze_backbone=freeze,
                    num_workers=args.num_workers,
                )
                results[f'{model_name}_{dataset_name}'] = acc
            except Exception as e:
                logger.error(f"训练失败: {model_name} on {dataset_name}: {e}", exc_info=True)
                results[f'{model_name}_{dataset_name}'] = None

    # 打印结果汇总
    logger.info(f"\n{'='*60}")
    logger.info("训练结果汇总")
    logger.info(f"{'='*60}")
    for key, acc in results.items():
        status = f"{acc:.4f}" if acc is not None else "FAILED"
        logger.info(f"  {key}: {status}")


if __name__ == '__main__':
    main()
