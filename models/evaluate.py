"""
测试集评估脚本
加载训练好的模型，在测试集上计算所有评估指标
"""
import json
import logging
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.dataset import ImageClassificationDataset
from models.custom_cnn import build_model as build_custom_cnn
from models.resnet50 import build_model as build_resnet50
from models.efficientnet import build_model as build_efficientnet
from models.vit import build_model as build_vit
from models.densenet import build_model as build_densenet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
SAVE_DIR = ROOT_DIR / 'saved_models'
PROCESSED_DIR = ROOT_DIR / 'data' / 'processed'

MODEL_BUILDERS = {
    'custom_cnn': build_custom_cnn,
    'resnet50': build_resnet50,
    'efficientnet_b1': build_efficientnet,
    'vit_b16': build_vit,
    'densenet121': build_densenet,
}

DATASET_CONFIGS = {
    'caltech101': PROCESSED_DIR / 'caltech101' / 'split_info.json',
    'oxford102': PROCESSED_DIR / 'oxford102' / 'split_info.json',
}


def get_val_transforms():
    """验证/测试用 transforms（无数据增强）"""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


@torch.no_grad()
def evaluate_model(model, dataloader, device):
    """在测试集上评估模型，返回全部指标"""
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []

    for inputs, labels in tqdm(dataloader, desc='Evaluating'):
        inputs = inputs.to(device)
        labels = labels.to(device)

        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1)
        _, preds = torch.max(outputs, 1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)

    # Top-5 Accuracy
    top5_preds = np.argsort(all_probs, axis=1)[:, -5:]
    top5_correct = np.array([l in p for l, p in zip(all_labels, top5_preds)])

    return {
        'accuracy': accuracy_score(all_labels, all_preds),
        'top5_accuracy': top5_correct.mean(),
        'precision_macro': precision_score(all_labels, all_preds, average='macro', zero_division=0),
        'recall_macro': recall_score(all_labels, all_preds, average='macro', zero_division=0),
        'f1_macro': f1_score(all_labels, all_preds, average='macro', zero_division=0),
        'predictions': all_preds.tolist(),
        'labels': all_labels.tolist(),
    }


def run_evaluation(model_name, dataset_name):
    """对单个模型在指定数据集上运行测试集评估"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"设备: {device}")

    # 加载数据
    split_file = DATASET_CONFIGS[dataset_name]
    with open(split_file, 'r') as f:
        split_info = json.load(f)

    num_classes = split_info['num_classes']

    # Oxford 102 test 集无标签，使用 valid 集作为替代
    if dataset_name == 'oxford102':
        test_split = 'valid'
        logger.info("Oxford 102 test 集无标签，使用 valid 集评估")
    else:
        test_split = 'test'

    dataset = ImageClassificationDataset(
        split_file, split=test_split, transform=get_val_transforms()
    )
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False,
                            num_workers=2, pin_memory=True)
    logger.info(f"测试集: {len(dataset)} 张图片, {num_classes} 类")

    # 加载模型
    ckpt_path = SAVE_DIR / f'{model_name}_{dataset_name}_best.pth'
    if not ckpt_path.exists():
        logger.error(f"模型文件不存在: {ckpt_path}")
        return None

    model = MODEL_BUILDERS[model_name](num_classes=num_classes)
    checkpoint = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    logger.info(f"加载模型: {ckpt_path} (训练 Acc: {checkpoint['accuracy']:.4f})")

    # 评估
    results = evaluate_model(model, dataloader, device)

    # 推理时间
    model.eval()
    dummy = torch.randn(1, 3, 224, 224).to(device)
    # Warm-up
    for _ in range(10):
        _ = model(dummy)
    torch.cuda.synchronize()
    import time
    start = time.perf_counter()
    for _ in range(100):
        _ = model(dummy)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    results['inference_time_ms'] = elapsed / 100 * 1000

    # 模型大小
    results['model_size_mb'] = ckpt_path.stat().st_size / (1024 * 1024)

    logger.info(f"Accuracy:      {results['accuracy']:.4f}")
    logger.info(f"Top-5 Acc:     {results['top5_accuracy']:.4f}")
    logger.info(f"Precision:     {results['precision_macro']:.4f}")
    logger.info(f"Recall:        {results['recall_macro']:.4f}")
    logger.info(f"F1 Score:      {results['f1_macro']:.4f}")
    logger.info(f"Inference:     {results['inference_time_ms']:.1f} ms")
    logger.info(f"Model Size:    {results['model_size_mb']:.1f} MB")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='测试集评估')
    parser.add_argument('--model', type=str, default='all',
                        choices=['all', 'custom_cnn', 'resnet50', 'efficientnet_b1',
                                 'vit_b16', 'densenet121'])
    parser.add_argument('--dataset', type=str, default='all',
                        choices=['all', 'caltech101', 'oxford102'])
    args = parser.parse_args()

    models = list(MODEL_BUILDERS.keys()) if args.model == 'all' else [args.model]
    datasets = list(DATASET_CONFIGS.keys()) if args.dataset == 'all' else [args.dataset]

    all_results = {}
    for ds in datasets:
        for m in models:
            logger.info(f"\n{'='*60}")
            logger.info(f"评估: {m} on {ds}")
            logger.info(f"{'='*60}")
            try:
                r = run_evaluation(m, ds)
                if r:
                    all_results[f'{m}_{ds}'] = r
            except Exception as e:
                logger.error(f"评估失败: {e}", exc_info=True)

    # 合并已有结果后保存
    out_path = ROOT_DIR / 'docs' / 'evaluation_results.json'
    if out_path.exists():
        with open(out_path) as f:
            existing = json.load(f)
        existing.update(all_results)
        all_results = existing
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    logger.info(f"\n评估结果已保存: {out_path}")

    # 打印汇总
    print("\n")
    print("=" * 100)
    print(f"{'Model':<20} {'Dataset':<15} {'Test Acc':>10} {'Top5 Acc':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Infer(ms)':>10} {'Size(MB)':>10}")
    print("-" * 100)
    for key, r in all_results.items():
        m, ds = key.rsplit('_', 1)
        print(f"{m:<20} {ds:<15} {r['accuracy']:>10.4f} {r['top5_accuracy']:>10.4f} "
              f"{r['precision_macro']:>10.4f} {r['recall_macro']:>10.4f} {r['f1_macro']:>10.4f} "
              f"{r['inference_time_ms']:>10.1f} {r['model_size_mb']:>10.1f}")
    print("=" * 100)


if __name__ == '__main__':
    main()
