"""
模型训练入口脚本 - 两阶段训练

迁移学习模型 (resnet50/efficientnet_b1/vit_b16/densenet121):
  阶段一: 冻结骨干，训练分类头 (15 epochs, lr=0.001)
  阶段二: 解冻骨干，全网络微调 (35 epochs, lr=0.0001)

自定义模型 (custom_cnn):
  从头训练 (50 epochs, lr=0.001)

用法:
  python models/train.py --model resnet50 --dataset caltech101
  python models/train.py --model all --dataset caltech101
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


# 模块级函数（供 transforms.Lambda 使用，需可被 pickle 序列化）
def _to_uint8(x):
    """float32 [0,1] → uint8 [0,255]"""
    return (x * 255).to(torch.uint8)


def _to_float32(x):
    """uint8 [0,255] → float32 [0,1]"""
    return x.to(torch.float32) / 255.0

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


def get_transforms(dataset_name, is_train=True, use_strong_aug=True):
    """获取数据增强/预处理 transforms（Caltech-101 使用强增强，Custom CNN 跳过）"""
    if is_train:
        # 阶段1: PIL Image 变换（在 ToTensor 之前）
        pil_transforms = [
            transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.15),
        ]
        # 阶段2: Tensor 变换（RandAugment 需要 uint8 输入）
        tensor_transforms = [
            transforms.ToTensor(),  # PIL → float32 [0,1]
        ]
        if dataset_name == 'caltech101' and use_strong_aug:
            # RandAugment 的 equalize/posterize/solarize 要求 uint8
            tensor_transforms += [
                transforms.Lambda(_to_uint8),
                transforms.RandAugment(num_ops=2, magnitude=9),
                transforms.Lambda(_to_float32),
                transforms.RandomErasing(p=0.3, scale=(0.02, 0.15)),
            ]
        tensor_transforms.append(
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        )
        return transforms.Compose(pil_transforms + tensor_transforms)
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])


def get_dataloaders(dataset_name, batch_size=32, num_workers=2, use_strong_aug=True):
    """创建数据加载器，返回 dataset 用于获取类别权重"""
    config = DATASET_CONFIGS[dataset_name]
    split_file = config['split_file']

    if not split_file.exists():
        raise FileNotFoundError(
            f"划分文件不存在: {split_file}\n"
            f"请先运行: python scripts/preprocess.py"
        )

    train_dataset = ImageClassificationDataset(
        split_file, split='train',
        transform=get_transforms(dataset_name, is_train=True,
                                 use_strong_aug=use_strong_aug),
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

    return train_loader, val_loader, train_dataset


def train_model(model_name, dataset_name, epochs=50, batch_size=32,
                lr=0.001, freeze_backbone=True, num_workers=2):
    """训练单个模型，迁移学习模型使用两阶段训练"""

    # 获取设备
    if torch.cuda.is_available():
        device = torch.device('cuda')
        logger.info(f"使用 GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        logger.info("使用 CPU")

    # 获取数据（dataset 用于类别权重）
    # Custom CNN 不使用强增强（RandAugment 对从零训练破坏力太大）
    _use_strong = (model_name != 'custom_cnn')
    train_loader, val_loader, train_dataset = get_dataloaders(
        dataset_name, batch_size, num_workers, use_strong_aug=_use_strong
    )
    num_classes = train_dataset.num_classes

    # Caltech-101 优化配置: 类别权重 + 标签平滑 + 强正则化
    if dataset_name == 'caltech101':
        class_weight = train_dataset.get_class_weights()
        label_smoothing = 0.1
        wd_phase1 = 1e-3   # 高权重衰减防过拟合
        wd_phase2 = 3e-3
        lr_phase2 = 5e-5   # 极低学习率保护预训练特征
        patience_phase2 = 8
        logger.info(f"Caltech-101 优化模式: 类别权重 + 标签平滑={label_smoothing} + RandAugment + RandomErasing")
    else:
        class_weight = None
        label_smoothing = 0.0
        wd_phase1 = 1e-4
        wd_phase2 = 1e-4
        lr_phase2 = 1e-4
        patience_phase2 = 10

    is_transfer = (model_name != 'custom_cnn')

    if is_transfer:
        # ============================================================
        # 阶段一: 冻结骨干，只训练分类头
        # ============================================================
        logger.info("\n" + "=" * 60)
        logger.info(f"阶段一: 冻结骨干网络，训练分类头 (Epoch 1-15)")
        logger.info("=" * 60)

        model = MODEL_BUILDERS[model_name](
            num_classes=num_classes, freeze_backbone=True
        )
        model = model.to(device)

        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"总参数: {total_params:,} | 可训练: {trainable_params:,}")

        trainer = Trainer(
            model=model, device=device,
            save_dir=SAVE_DIR,
            model_name=model_name,
            dataset_name=dataset_name,
        )

        trainer.train(
            train_loader=train_loader, val_loader=val_loader,
            epochs=15, lr=0.001, weight_decay=wd_phase1,
            scheduler_patience=3, early_stop_patience=5,
            class_weight=class_weight, label_smoothing=label_smoothing,
        )

        phase1_best = trainer.best_acc
        logger.info(f"阶段一完成! 最佳 Val Acc: {phase1_best:.4f}")

        # ============================================================
        # 阶段二: 解冻骨干，全网络微调
        # ============================================================
        logger.info("\n" + "=" * 60)
        logger.info(f"阶段二: 解冻骨干网络，全网络微调 (Epoch 16-{epochs})")
        logger.info("=" * 60)

        # 加载阶段一最佳权重
        best_path = SAVE_DIR / f'{model_name}_{dataset_name}_best.pth'
        if best_path.exists():
            checkpoint = torch.load(best_path, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"加载阶段一最佳权重 (Acc: {checkpoint['accuracy']:.4f})")

        # 解冻骨干
        model.unfreeze_backbone()
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"可训练参数: {trainable_params:,} (全部解冻)")

        trainer.train(
            train_loader=train_loader, val_loader=val_loader,
            epochs=epochs - 15, lr=lr_phase2, weight_decay=wd_phase2,
            scheduler_patience=5, early_stop_patience=patience_phase2,
            class_weight=class_weight, label_smoothing=label_smoothing,
        )

        final_best = trainer.best_acc
        logger.info(f"阶段二完成! 最佳 Val Acc: {final_best:.4f}")

    else:
        # ============================================================
        # Custom CNN: 从头训练
        # ============================================================
        logger.info("\n" + "=" * 60)
        logger.info(f"Custom CNN: 从头训练 {epochs} 轮")
        logger.info("=" * 60)

        model = MODEL_BUILDERS[model_name](num_classes=num_classes)
        model = model.to(device)

        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"总参数: {total_params:,} | 可训练: {trainable_params:,}")

        trainer = Trainer(
            model=model, device=device,
            save_dir=SAVE_DIR,
            model_name=model_name,
            dataset_name=dataset_name,
        )

        # Custom CNN 从零训练：不适用类别权重和标签平滑（会破坏梯度）
        trainer.train(
            train_loader=train_loader, val_loader=val_loader,
            epochs=epochs, lr=0.001, weight_decay=1e-4,
            scheduler_patience=5, early_stop_patience=10,
            class_weight=None, label_smoothing=0.0,
        )

        final_best = trainer.best_acc

    # 保存训练历史
    trainer.save_history()

    return final_best


def main():
    parser = argparse.ArgumentParser(
        description='训练图像分类模型（迁移学习自动使用两阶段训练）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python models/train.py --model resnet50 --dataset caltech101
  python models/train.py --model all --dataset caltech101
  python models/train.py --model all --dataset all
        """
    )
    parser.add_argument('--model', type=str, default='resnet50',
                        choices=['all', 'custom_cnn', 'resnet50', 'efficientnet_b1',
                                 'vit_b16', 'densenet121'],
                        help='模型名称')
    parser.add_argument('--dataset', type=str, default='caltech101',
                        choices=['all', 'caltech101', 'oxford102'],
                        help='数据集名称')
    parser.add_argument('--epochs', type=int, default=50,
                        help='总训练轮数（迁移学习=阶段一15+阶段二35）')
    parser.add_argument('--batch_size', type=int, default=None,
                        help='批次大小（默认: 32, ViT: 16）')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='初始学习率')
    parser.add_argument('--num_workers', type=int, default=2,
                        help='数据加载线程数')

    args = parser.parse_args()

    # 确定要训练的模型和数据集
    models_to_train = list(MODEL_BUILDERS.keys()) if args.model == 'all' else [args.model]
    datasets_to_train = list(DATASET_CONFIGS.keys()) if args.dataset == 'all' else [args.dataset]

    results = {}

    for dataset_name in datasets_to_train:
        for model_name in models_to_train:
            logger.info(f"\n{'='*60}")
            logger.info(f"训练: {model_name} on {dataset_name}")
            logger.info(f"{'='*60}\n")

            # 自动调整 batch_size（ViT 显存需求大）
            if args.batch_size is not None:
                bs = args.batch_size
            elif model_name == 'vit_b16':
                bs = 16
            else:
                bs = 32

            try:
                acc = train_model(
                    model_name=model_name,
                    dataset_name=dataset_name,
                    epochs=args.epochs,
                    batch_size=bs,
                    lr=args.lr,
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
