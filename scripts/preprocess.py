"""
数据预处理脚本
- 重命名异常文件
- Caltech-101: 划分 train/val/test，创建标签映射
- Oxford 102: 整理元数据，处理测试集
- 计算数据集统计信息（均值/标准差）
- 创建 PyTorch Dataset 类
"""
import os
import json
import shutil
import logging
from pathlib import Path
from collections import defaultdict

import numpy as np
from PIL import Image
from tqdm import tqdm
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / 'data' / 'raw'
PROCESSED_DIR = ROOT_DIR / 'data' / 'processed'

# 图像参数
IMG_SIZE = 224
RANDOM_SEED = 42


def rename_anomalous_file():
    """重命名 Caltech-101 中的异常文件 BACKGROUND_Google/tmp → tmp.jpg"""
    old_path = RAW_DIR / 'caltech-101 dataset' / 'caltech-101' / 'BACKGROUND_Google' / 'tmp'
    new_path = RAW_DIR / 'caltech-101 dataset' / 'caltech-101' / 'BACKGROUND_Google' / 'tmp.jpg'

    if old_path.exists() and not new_path.exists():
        old_path.rename(new_path)
        logger.info(f"✓ 已重命名: {old_path} → {new_path}")
    elif new_path.exists():
        logger.info(f"→ 文件已是正确名称: {new_path}")
    else:
        logger.warning(f"⚠ 未找到异常文件: {old_path}")


def process_caltech101():
    """
    处理 Caltech-101 数据集:
    1. 扫描所有类目录
    2. 创建标签映射 (class_name → class_id)
    3. 按 70/15/15 划分 train/val/test（分层采样）
    4. 保存划分信息为 JSON
    """
    logger.info("=" * 60)
    logger.info("处理 Caltech-101 数据集")
    logger.info("=" * 60)

    dataset_dir = RAW_DIR / 'caltech-101 dataset' / 'caltech-101'
    output_dir = PROCESSED_DIR / 'caltech101'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有类目录（排除非目录文件）
    class_dirs = sorted([
        d for d in dataset_dir.iterdir()
        if d.is_dir() and d.name != 'BACKGROUND_Google'
    ])

    # 创建标签映射
    class_to_idx = {d.name: i for i, d in enumerate(class_dirs)}
    idx_to_class = {i: d.name for i, d in enumerate(class_dirs)}

    logger.info(f"类别数: {len(class_dirs)}")
    logger.info(f"标签映射已创建: {len(class_to_idx)} 个类别")

    # 收集所有图片路径和标签
    all_images = []
    class_counts = {}

    for class_dir in class_dirs:
        images = sorted([
            str(p) for p in class_dir.iterdir()
            if p.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ])
        class_name = class_dir.name
        class_counts[class_name] = len(images)
        for img_path in images:
            all_images.append({
                'path': img_path,
                'class_name': class_name,
                'class_id': class_to_idx[class_name],
            })

    logger.info(f"总图片数: {len(all_images)}")
    logger.info(f"最少类别: {min(class_counts, key=class_counts.get)} ({min(class_counts.values())} 张)")
    logger.info(f"最多类别: {max(class_counts, key=class_counts.get)} ({max(class_counts.values())} 张)")

    # 划分 train/val/test (70/15/15) - 分层采样
    labels = [item['class_id'] for item in all_images]

    # 先分出 train (70%) 和 temp (30%)
    train_indices, temp_indices = train_test_split(
        range(len(all_images)),
        test_size=0.30,
        stratify=labels,
        random_state=RANDOM_SEED,
    )

    # 再从 temp 分出 val (50% of temp = 15%) 和 test (50% of temp = 15%)
    temp_labels = [labels[i] for i in temp_indices]
    val_indices_rel, test_indices_rel = train_test_split(
        range(len(temp_indices)),
        test_size=0.50,
        stratify=temp_labels,
        random_state=RANDOM_SEED,
    )

    val_indices = [temp_indices[i] for i in val_indices_rel]
    test_indices = [temp_indices[i] for i in test_indices_rel]

    splits = {
        'train': [all_images[i] for i in train_indices],
        'val': [all_images[i] for i in val_indices],
        'test': [all_images[i] for i in test_indices],
    }

    for split_name, split_data in splits.items():
        logger.info(f"  {split_name}: {len(split_data)} 张图片")

    # 保存划分信息
    split_info = {
        'dataset': 'caltech101',
        'num_classes': len(class_dirs),
        'class_to_idx': class_to_idx,
        'idx_to_class': idx_to_class,
        'class_counts': class_counts,
        'splits': {
            split_name: [
                {
                    'path': item['path'],
                    'class_name': item['class_name'],
                    'class_id': item['class_id'],
                }
                for item in split_data
            ]
            for split_name, split_data in splits.items()
        },
    }

    split_file = output_dir / 'split_info.json'
    with open(split_file, 'w', encoding='utf-8') as f:
        json.dump(split_info, f, ensure_ascii=False, indent=2)
    logger.info(f"划分信息已保存至: {split_file}")

    return split_info


def process_oxford102():
    """
    处理 Oxford 102 Flower 数据集:
    1. 读取 cat_to_name.json 标签映射
    2. 整理 train/valid/test 路径
    3. 保存划分信息为 JSON
    """
    logger.info("=" * 60)
    logger.info("处理 Oxford 102 Flower 数据集")
    logger.info("=" * 60)

    dataset_dir = RAW_DIR / 'Oxford 102 Flower Dataset' / 'dataset'
    cat_to_name_file = RAW_DIR / 'Oxford 102 Flower Dataset' / 'cat_to_name.json'
    submission_file = RAW_DIR / 'Oxford 102 Flower Dataset' / 'sample_submission.csv'

    output_dir = PROCESSED_DIR / 'oxford102'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取类别名称映射
    with open(cat_to_name_file, 'r', encoding='utf-8') as f:
        cat_to_name = json.load(f)

    # 转换为 int key，并转为 0-indexed (原目录名为 1-102)
    cat_to_name = {int(k): v for k, v in cat_to_name.items()}
    # 创建 0-indexed 映射: 原始ID(1-102) → 0-indexed ID(0-101)
    original_to_zero = {orig: i for i, orig in enumerate(sorted(cat_to_name.keys()))}
    idx_to_class = {i: cat_to_name[orig] for orig, i in original_to_zero.items()}
    num_classes = len(cat_to_name)
    logger.info(f"类别数: {num_classes}")
    logger.info(f"类别名称映射已加载 (已转为 0-indexed)")

    # 处理 train 目录
    train_dir = dataset_dir / 'train'
    train_images = []
    class_counts = defaultdict(int)

    for class_dir in sorted(train_dir.iterdir(), key=lambda d: int(d.name)):
        if not class_dir.is_dir():
            continue
        original_id = int(class_dir.name)
        class_id = original_to_zero[original_id]  # 转为 0-indexed
        class_name = cat_to_name.get(original_id, f'class_{original_id}')
        images = sorted([
            str(p) for p in class_dir.iterdir()
            if p.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ])
        class_counts[class_id] += len(images)
        for img_path in images:
            train_images.append({
                'path': img_path,
                'class_id': class_id,
                'class_name': class_name,
            })

    # 处理 valid 目录
    valid_dir = dataset_dir / 'valid'
    valid_images = []

    for class_dir in sorted(valid_dir.iterdir(), key=lambda d: int(d.name)):
        if not class_dir.is_dir():
            continue
        original_id = int(class_dir.name)
        class_id = original_to_zero[original_id]  # 转为 0-indexed
        class_name = cat_to_name.get(original_id, f'class_{original_id}')
        images = sorted([
            str(p) for p in class_dir.iterdir()
            if p.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ])
        class_counts[class_id] += len(images)
        for img_path in images:
            valid_images.append({
                'path': img_path,
                'class_id': class_id,
                'class_name': class_name,
            })

    # 处理 test 目录（扁平目录，无子目录）
    test_dir = dataset_dir / 'test'
    test_images = []

    if test_dir.exists():
        image_files = sorted([
            p for p in test_dir.iterdir()
            if p.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ])
        # test 集的标签来自 sample_submission.csv
        # 但由于 sample_submission.csv 中 id 都是 0（占位符），test 集实际无标签
        logger.info(f"Test 集图片数: {len(image_files)} (无标签，用于最终预测)")
        for img_path in image_files:
            test_images.append({
                'path': str(img_path),
                'class_id': -1,  # 未知标签
                'class_name': 'unknown',
            })

    logger.info(f"Train: {len(train_images)} 张图片")
    logger.info(f"Valid: {len(valid_images)} 张图片")
    logger.info(f"Test: {len(test_images)} 张图片 (无标签)")
    logger.info(f"最少类别: {min(class_counts.values())} 张")
    logger.info(f"最多类别: {max(class_counts.values())} 张")

    # 保存划分信息
    split_info = {
        'dataset': 'oxford102',
        'num_classes': num_classes,
        'cat_to_name': {str(k): v for k, v in idx_to_class.items()},
        'idx_to_class': {str(k): v for k, v in idx_to_class.items()},
        'class_counts': {str(k): v for k, v in class_counts.items()},
        'splits': {
            'train': train_images,
            'valid': valid_images,
            'test': test_images,
        },
    }

    split_file = output_dir / 'split_info.json'
    with open(split_file, 'w', encoding='utf-8') as f:
        json.dump(split_info, f, ensure_ascii=False, indent=2)
    logger.info(f"划分信息已保存至: {split_file}")

    return split_info


def compute_dataset_stats(split_info, dataset_name, max_samples=2000):
    """
    计算数据集的均值和标准差（用于归一化）
    采样计算以节省时间
    """
    logger.info(f"计算 {dataset_name} 数据集统计信息（采样 {max_samples} 张）...")

    train_images = split_info['splits']['train']
    sample_size = min(max_samples, len(train_images))

    import random
    random.seed(RANDOM_SEED)
    sampled = random.sample(train_images, sample_size)

    mean_sum = np.zeros(3)
    std_sum = np.zeros(3)

    for item in tqdm(sampled, desc=f'计算 {dataset_name} 统计信息'):
        img = Image.open(item['path']).convert('RGB')
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
        img_array = np.array(img, dtype=np.float64) / 255.0

        mean_sum += img_array.mean(axis=(0, 1))
        std_sum += img_array.std(axis=(0, 1))

    mean = mean_sum / len(sampled)
    std = std_sum / len(sampled)

    logger.info(f"  Mean (RGB): [{mean[0]:.4f}, {mean[1]:.4f}, {mean[2]:.4f}]")
    logger.info(f"  Std  (RGB): [{std[0]:.4f}, {std[1]:.4f}, {std[2]:.4f}]")

    return {'mean': mean.tolist(), 'std': std.tolist()}


def main():
    """主函数：执行所有预处理步骤"""
    logger.info("=" * 60)
    logger.info("开始数据预处理")
    logger.info("=" * 60)

    # 1. 重命名异常文件
    rename_anomalous_file()

    # 2. 处理 Caltech-101
    caltech_info = process_caltech101()

    # 3. 处理 Oxford 102
    oxford_info = process_oxford102()

    # 4. 计算统计信息
    caltech_stats = compute_dataset_stats(caltech_info, 'caltech101')
    oxford_stats = compute_dataset_stats(oxford_info, 'oxford102')

    # 5. 保存统计信息
    stats = {
        'caltech101': caltech_stats,
        'oxford102': oxford_stats,
        'img_size': IMG_SIZE,
    }
    stats_file = PROCESSED_DIR / 'dataset_stats.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"统计信息已保存至: {stats_file}")

    logger.info("=" * 60)
    logger.info("数据预处理完成!")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
