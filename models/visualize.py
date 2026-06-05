"""
训练过程可视化脚本 — 损失曲线、准确率曲线、模型对比分析图
输出保存至 docs/figures/ 目录
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

ROOT = Path(__file__).resolve().parent.parent
SAVE_DIR = ROOT / 'saved_models'
OUT_DIR = ROOT / 'docs' / 'figures'
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = ['custom_cnn', 'resnet50', 'efficientnet_b1', 'vit_b16', 'densenet121']
MODEL_NAMES = {
    'custom_cnn': 'Custom CNN',
    'resnet50': 'ResNet-50',
    'efficientnet_b1': 'EfficientNet-B1',
    'vit_b16': 'ViT-B/16',
    'densenet121': 'DenseNet-121',
}
DATASETS = ['caltech101', 'oxford102']
DATASET_NAMES = {'caltech101': 'Caltech-101', 'oxford102': 'Oxford 102'}
COLORS = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12']


def load_history(model, dataset):
    """加载训练历史"""
    path = SAVE_DIR / f'{model}_{dataset}_history.json'
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def plot_training_curves():
    """
    图1: 训练曲线 — 每个模型单独的 Loss + Accuracy 子图
    """
    fig, axes = plt.subplots(5, 4, figsize=(20, 28))
    fig.suptitle('Training Curves — Loss & Accuracy', fontsize=18, fontweight='bold', y=0.995)

    for i, model in enumerate(MODELS):
        for j, dataset in enumerate(DATASETS):
            h = load_history(model, dataset)
            if h is None:
                continue

            epochs = list(range(1, len(h['train_loss']) + 1))

            # Loss 子图
            ax_loss = axes[i][j * 2]
            ax_loss.plot(epochs, h['train_loss'], color=COLORS[i], alpha=0.7, linewidth=1.5, label='Train Loss')
            ax_loss.plot(epochs, h['val_loss'], color=COLORS[i], alpha=1.0, linewidth=2.0, linestyle='--', label='Val Loss')
            ax_loss.set_title(f'{MODEL_NAMES[model]} — {DATASET_NAMES[dataset]} Loss', fontsize=11)
            ax_loss.set_xlabel('Epoch')
            ax_loss.set_ylabel('Loss')
            ax_loss.legend(fontsize=8, loc='upper right')
            ax_loss.grid(True, alpha=0.3)

            # Accuracy 子图
            ax_acc = axes[i][j * 2 + 1]
            ax_acc.plot(epochs, h['train_acc'], color=COLORS[i], alpha=0.7, linewidth=1.5, label='Train Acc')
            ax_acc.plot(epochs, h['val_acc'], color=COLORS[i], alpha=1.0, linewidth=2.0, linestyle='--', label='Val Acc')
            # 标注最佳点
            best_ep = h.get('best_epoch', 0) - 1
            if 0 <= best_ep < len(h['val_acc']):
                ax_acc.scatter(best_ep + 1, h['val_acc'][best_ep], c=COLORS[i], s=80, zorder=5,
                               edgecolors='black', linewidths=1)
                ax_acc.annotate(f'{h["val_acc"][best_ep]:.3f}',
                                (best_ep + 1, h['val_acc'][best_ep]),
                                textcoords="offset points", xytext=(0, 12),
                                ha='center', fontsize=8, fontweight='bold')
            ax_acc.set_title(f'{MODEL_NAMES[model]} — {DATASET_NAMES[dataset]} Accuracy', fontsize=11)
            ax_acc.set_xlabel('Epoch')
            ax_acc.set_ylabel('Accuracy')
            ax_acc.legend(fontsize=8, loc='lower right')
            ax_acc.grid(True, alpha=0.3)

    plt.tight_layout()
    path = OUT_DIR / 'training_curves.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'[OK] {path}')


def plot_comparison_bar():
    """
    图2: 测试准确率对比柱状图
    """
    eval_path = ROOT / 'docs' / 'evaluation_results.json'
    if not eval_path.exists():
        print('[SKIP] evaluation_results.json not found')
        return

    with open(eval_path) as f:
        results = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Model Accuracy Comparison — Test Set', fontsize=18, fontweight='bold')

    for j, dataset in enumerate(DATASETS):
        ax = axes[j]
        accs = []
        labels = []
        for model in MODELS:
            key = f'{model}_{dataset}'
            if key in results:
                accs.append(results[key]['accuracy'])
                labels.append(MODEL_NAMES[model])

        bars = ax.bar(range(len(labels)), accs, color=COLORS[:len(labels)], edgecolor='white', linewidth=1.2)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=10)
        ax.set_ylabel('Accuracy', fontsize=13)
        ax.set_title(f'{DATASET_NAMES[dataset]}', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.08)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter(1.0))
        ax.grid(axis='y', alpha=0.3)

        # 标注数值
        for bar, acc in zip(bars, accs):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{acc*100:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # 画 90% 和 95% 参考线
        ax.axhline(y=0.90, color='orange', linestyle=':', linewidth=1.5, alpha=0.7, label='90% baseline')
        ax.axhline(y=0.95, color='green', linestyle=':', linewidth=1.5, alpha=0.7, label='95% target')
        ax.legend(fontsize=9)

    plt.tight_layout()
    path = OUT_DIR / 'accuracy_comparison.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'[OK] {path}')


def plot_efficiency_scatter():
    """
    图3: 效率分析 — 参数量 vs 准确率 + 推理速度 vs 准确率
    """
    eval_path = ROOT / 'docs' / 'evaluation_results.json'
    if not eval_path.exists():
        print('[SKIP] evaluation_results.json not found')
        return

    with open(eval_path) as f:
        results = json.load(f)

    # 模型参数量和指标
    param_info = {
        'custom_cnn': {'params': 31.0, 'infer': 1.9},
        'resnet50': {'params': 23.5, 'infer': 7.1},
        'efficientnet_b1': {'params': 6.5, 'infer': 18.5},
        'vit_b16': {'params': 85.9, 'infer': 17.9},
        'densenet121': {'params': 7.0, 'infer': 19.3},
    }

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for dataset_idx, dataset in enumerate(DATASETS):
        ax = axes[dataset_idx]
        xs, ys, names, sizes = [], [], [], []
        for model in MODELS:
            key = f'{model}_{dataset}'
            if key in results:
                xs.append(param_info[model]['params'])
                ys.append(results[key]['accuracy'] * 100)
                names.append(MODEL_NAMES[model])
                sizes.append(max(60, param_info[model]['params'] * 2.5))

        scatter = ax.scatter(xs, ys, s=sizes, c=COLORS[:len(xs)], alpha=0.8,
                             edgecolors='black', linewidths=1)
        for x, y, name in zip(xs, ys, names):
            ax.annotate(name, (x, y), textcoords="offset points", xytext=(0, 12),
                        ha='center', fontsize=9, fontweight='bold')

        ax.set_xlabel('Parameters (M)', fontsize=12)
        ax.set_ylabel('Test Accuracy (%)', fontsize=12)
        ax.set_title(f'{DATASET_NAMES[dataset]} — Efficiency Analysis', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=90, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
        ax.axhline(y=95, color='green', linestyle=':', linewidth=1.5, alpha=0.7)

    plt.tight_layout()
    path = OUT_DIR / 'efficiency_analysis.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'[OK] {path}')


def plot_radar():
    """
    图4: 雷达图 — 多维度综合评分（归一化到 0-1）
    """
    eval_path = ROOT / 'docs' / 'evaluation_results.json'
    if not eval_path.exists():
        print('[SKIP] evaluation_results.json not found')
        return

    with open(eval_path) as f:
        results = json.load(f)

    categories = ['Accuracy', 'Top-5 Acc', 'F1 Score', 'Speed', 'Compactness']
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, axes = plt.subplots(1, 2, figsize=(16, 8), subplot_kw=dict(polar=True))

    for j, dataset in enumerate(DATASETS):
        ax = axes[j]
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)

        for i, model in enumerate(MODELS):
            key = f'{model}_{dataset}'
            if key not in results:
                continue
            r = results[key]
            # 归一化: Accuracy / 1.0, Speed: 1/(1+ms), Size: 1/(1+MB/10)
            values = [
                r['accuracy'],
                r['top5_accuracy'],
                r['f1_macro'],
                1.0 / (1.0 + r.get('inference_time_ms', 10) / 10),
                1.0 / (1.0 + r.get('model_size_mb', 100) / 20),
            ]
            values += values[:1]
            ax.fill(angles, values, color=COLORS[i], alpha=0.15)
            ax.plot(angles, values, color=COLORS[i], linewidth=2, label=MODEL_NAMES[model])

        ax.set_title(f'{DATASET_NAMES[dataset]}', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)

    plt.tight_layout()
    path = OUT_DIR / 'radar_comparison.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'[OK] {path}')


def plot_summary_table():
    """
    图5: 汇总对比表 — 表格形式的最终结果
    """
    eval_path = ROOT / 'docs' / 'evaluation_results.json'
    if not eval_path.exists():
        print('[SKIP] evaluation_results.json not found')
        return

    with open(eval_path) as f:
        results = json.load(f)

    fig, ax = plt.subplots(figsize=(18, 6))
    ax.axis('off')

    col_labels = ['Model', 'Acc', 'Top-5', 'F1', 'ms', 'MB',
                  'Acc', 'Top-5', 'F1', 'ms', 'MB']
    rows = []
    for model in MODELS:
        row = [MODEL_NAMES[model]]
        for dataset in DATASETS:
            key = f'{model}_{dataset}'
            if key in results:
                r = results[key]
                row += [f"{r['accuracy']*100:.1f}%", f"{r['top5_accuracy']*100:.1f}%",
                        f"{r['f1_macro']:.3f}", f"{r['inference_time_ms']:.1f}",
                        f"{r['model_size_mb']:.1f}"]
            else:
                row += ['—'] * 5
        rows.append(row)

    # 双表头
    header_top = ['', 'Caltech-101', '', '', '', '', '', 'Oxford 102', '', '', '', '']
    header_sub = ['Model', 'Acc', 'Top-5', 'F1', 'ms', 'MB',
                  'Model', 'Acc', 'Top-5', 'F1', 'ms', 'MB']

    # 简化：单一表头
    table = ax.table(cellText=rows, colLabels=col_labels, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.6)

    # 表头样式
    for i in range(len(col_labels)):
        table[0, i].set_facecolor('#2c3e50')
        table[0, i].set_text_props(color='white', fontweight='bold')

    # 数据行交替着色
    for i in range(len(rows)):
        for j in range(len(col_labels)):
            if i % 2 == 0:
                table[i + 1, j].set_facecolor('#ecf0f1')
            if j == 0 or j == 6:
                table[i + 1, j].set_text_props(fontweight='bold')

    ax.set_title('Final Evaluation Results Summary', fontsize=16, fontweight='bold', pad=20)

    plt.tight_layout()
    path = OUT_DIR / 'summary_table.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'[OK] {path}')


def plot_confusion_matrices():
    """
    图6: 混淆矩阵 — 每数据集最佳模型 + 全部模型
    """
    import sys
    sys.path.insert(0, str(ROOT))

    import torch
    from torch.utils.data import DataLoader
    from torchvision import transforms
    from sklearn.metrics import confusion_matrix
    from models.dataset import ImageClassificationDataset
    from models.custom_cnn import build_model as build_custom_cnn
    from models.resnet50 import build_model as build_resnet50
    from models.efficientnet import build_model as build_efficientnet
    from models.vit import build_model as build_vit
    from models.densenet import build_model as build_densenet

    builders = {
        'custom_cnn': build_custom_cnn,
        'resnet50': build_resnet50,
        'efficientnet_b1': build_efficientnet,
        'vit_b16': build_vit,
        'densenet121': build_densenet,
    }

    val_transform = transforms.Compose([
        transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    for dataset in DATASETS:
        split_file = ROOT / 'data' / 'processed' / dataset / 'split_info.json'
        with open(split_file) as f:
            info = json.load(f)

        num_classes = info['num_classes']
        test_split = 'valid' if dataset == 'oxford102' else 'test'

        # 获取类名（取前15个字符）
        if dataset == 'caltech101':
            class_names = [info['idx_to_class'][str(i)][:15] for i in range(num_classes)]
        else:
            class_names = [info['idx_to_class'].get(str(i), f'cls_{i}')[:15] for i in range(num_classes)]

        dataset_obj = ImageClassificationDataset(split_file, split=test_split, transform=val_transform)
        loader = DataLoader(dataset_obj, batch_size=32, shuffle=False, num_workers=2, pin_memory=True)

        # 每个模型生成混淆矩阵
        for model_name in MODELS:
            ckpt_path = SAVE_DIR / f'{model_name}_{dataset}_best.pth'
            if not ckpt_path.exists():
                continue

            print(f'  Confusion Matrix: {model_name} on {dataset} ({num_classes} classes)...')

            model = builders[model_name](num_classes=num_classes)
            ckpt = torch.load(ckpt_path, map_location=device)
            model.load_state_dict(ckpt['model_state_dict'])
            model = model.to(device)
            model.eval()

            all_preds, all_labels = [], []
            with torch.no_grad():
                for inputs, labels in loader:
                    outputs = model(inputs.to(device))
                    all_preds.extend(outputs.argmax(1).cpu().numpy())
                    all_labels.extend(labels.numpy())

            cm = confusion_matrix(all_labels, all_preds, labels=range(num_classes))
            # 按行归一化
            cm_norm = cm.astype('float32') / cm.sum(axis=1, keepdims=True).clip(min=1)

            # 绘图 — 101/102类只画缩略图
            fig, ax = plt.subplots(figsize=(18, 16))
            im = ax.imshow(cm_norm, cmap='Blues', aspect='auto', vmin=0, vmax=1)
            ax.set_title(f'Confusion Matrix — {MODEL_NAMES[model_name]} on {DATASET_NAMES[dataset]}\n'
                         f'(Test Acc: {ckpt["accuracy"]:.3f})',
                         fontsize=14, fontweight='bold')
            ax.set_xlabel('Predicted', fontsize=12)
            ax.set_ylabel('True', fontsize=12)

            # 刻度标签（类别太多时稀疏显示）
            step = max(1, num_classes // 20)
            ticks = list(range(0, num_classes, step))
            ax.set_xticks(ticks)
            ax.set_yticks(ticks)
            ax.set_xticklabels([class_names[t] for t in ticks], rotation=90, fontsize=5)
            ax.set_yticklabels([class_names[t] for t in ticks], fontsize=5)

            plt.colorbar(im, ax=ax, shrink=0.8, label='Normalized Accuracy')
            plt.tight_layout()

            path = OUT_DIR / f'confusion_{model_name}_{dataset}.png'
            fig.savefig(path, dpi=120, bbox_inches='tight')
            plt.close()
            print(f'    [OK] {path}')

    # 额外: 最佳模型的高清大图（Caltech-101: EfficientNet-B1, Oxford 102: DenseNet-121）
    for dataset, best_model in [('caltech101', 'efficientnet_b1'), ('oxford102', 'densenet121')]:
        _plot_single_confusion_highlight(dataset, best_model, builders, device,
                                         val_transform, class_names if dataset == 'caltech101' else None)


def _plot_single_confusion_highlight(dataset, model_name, builders, device, val_transform, class_names):
    """为单个最佳模型画高亮混淆矩阵（标注易混淆类对）"""
    import torch
    from torch.utils.data import DataLoader
    from sklearn.metrics import confusion_matrix
    from models.dataset import ImageClassificationDataset

    split_file = ROOT / 'data' / 'processed' / dataset / 'split_info.json'
    with open(split_file) as f:
        info = json.load(f)

    num_classes = info['num_classes']
    test_split = 'valid' if dataset == 'oxford102' else 'test'

    if class_names is None:
        class_names = [info['idx_to_class'].get(str(i), f'cls_{i}')[:15] for i in range(num_classes)]

    dataset_obj = ImageClassificationDataset(split_file, split=test_split, transform=val_transform)
    loader = DataLoader(dataset_obj, batch_size=32, shuffle=False, num_workers=2, pin_memory=True)

    ckpt_path = SAVE_DIR / f'{model_name}_{dataset}_best.pth'
    model = builders[model_name](num_classes=num_classes)
    ckpt = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(ckpt['model_state_dict'])
    model = model.to(device)
    model.eval()

    all_preds, all_labels = [], []
    with torch.no_grad():
        for inputs, labels in loader:
            outputs = model(inputs.to(device))
            all_preds.extend(outputs.argmax(1).cpu().numpy())
            all_labels.extend(labels.numpy())

    cm = confusion_matrix(all_labels, all_preds, labels=range(num_classes))
    cm_norm = cm.astype('float32') / cm.sum(axis=1, keepdims=True).clip(min=1)

    # 找 top 10 最易混淆类对（非对角线最大值）
    cm_off = cm_norm.copy()
    np.fill_diagonal(cm_off, 0)
    top_pairs = []
    flat_indices = np.argsort(cm_off.ravel())[-10:]
    for idx in flat_indices:
        i, j = np.unravel_index(idx, cm_off.shape)
        top_pairs.append((i, j, cm_off[i, j]))

    fig, ax = plt.subplots(figsize=(20, 18))
    im = ax.imshow(cm_norm, cmap='Blues', aspect='auto', vmin=0, vmax=1)
    ax.set_title(f'Confusion Matrix (Best Model) — {MODEL_NAMES[model_name]} on {DATASET_NAMES[dataset]}\n'
                 f'Test Acc: {ckpt["accuracy"]*100:.1f}%  |  Top-10 confused pairs marked with ★',
                 fontsize=14, fontweight='bold')

    # 标注易混淆类对
    for i, j, v in top_pairs:
        ax.annotate('★', (j, i), ha='center', va='center', fontsize=10, color='red', fontweight='bold')

    step = max(1, num_classes // 20)
    ticks = list(range(0, num_classes, step))
    ax.set_xticks(ticks); ax.set_yticks(ticks)
    ax.set_xticklabels([class_names[t] for t in ticks], rotation=90, fontsize=6)
    ax.set_yticklabels([class_names[t] for t in ticks], fontsize=6)
    ax.set_xlabel('Predicted', fontsize=13)
    ax.set_ylabel('True', fontsize=13)

    plt.colorbar(im, ax=ax, shrink=0.8, label='Normalized Accuracy')
    plt.tight_layout()

    path = OUT_DIR / f'confusion_best_{model_name}_{dataset}.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'    [OK] {path} (highlighted)')


def plot_prediction_samples():
    """
    图7: 预测结果可视化 — 测试集样本展示（真实标签 vs 预测标签）
    每个数据集的最佳模型，展示正确和错误预测样本
    """
    import sys
    sys.path.insert(0, str(ROOT))

    import random
    import torch
    from torchvision import transforms
    from models.efficientnet import build_model as build_efficientnet
    from models.densenet import build_model as build_densenet
    from PIL import Image

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    infer_transform = transforms.Compose([
        transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 最佳模型配置
    configs = [
        ('caltech101', 'efficientnet_b1', build_efficientnet),
        ('oxford102', 'densenet121', build_densenet),
    ]

    for dataset, model_name, builder in configs:
        split_file = ROOT / 'data' / 'processed' / dataset / 'split_info.json'
        with open(split_file) as f:
            info = json.load(f)

        num_classes = info['num_classes']
        test_split = 'valid' if dataset == 'oxford102' else 'test'

        # 类名映射
        if dataset == 'caltech101':
            idx_to_class = {int(k): v for k, v in info['idx_to_class'].items()}
        else:
            idx_to_class = {int(k): v for k, v in info.get('idx_to_class', {}).items()}

        # 加载模型
        ckpt_path = SAVE_DIR / f'{model_name}_{dataset}_best.pth'
        model = builder(num_classes=num_classes)
        ckpt = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        model = model.to(device)
        model.eval()

        # 获取测试集样本列表
        samples = info['splits'][test_split]
        random.seed(42)
        random.shuffle(samples)

        correct_samples = []
        wrong_samples = []

        for sample in samples:
            img_path = sample['path']
            true_id = sample['class_id']

            try:
                img = Image.open(img_path).convert('RGB')
                tensor = infer_transform(img).unsqueeze(0).to(device)

                with torch.no_grad():
                    output = model(tensor)
                    prob = torch.softmax(output, dim=1)
                    conf, pred_id = prob.max(dim=1)
                    pred_id = pred_id.item()
                    conf = conf.item()

                entry = (img_path, true_id, pred_id, conf)
                if pred_id == true_id:
                    if len(correct_samples) < 30:
                        correct_samples.append(entry)
                else:
                    if len(wrong_samples) < 10:
                        wrong_samples.append(entry)

                if len(correct_samples) >= 30 and len(wrong_samples) >= 10:
                    break

            except Exception:
                continue

        print(f"  {MODEL_NAMES[model_name]} on {DATASET_NAMES[dataset]}: "
              f"{len(correct_samples)} correct, {len(wrong_samples)} wrong samples")

        # 绘制图表: 3行 × 10列
        n_correct = min(20, len(correct_samples))
        n_wrong = min(10, len(wrong_samples))
        fig, axes = plt.subplots(3, 10, figsize=(24, 9))
        fig.suptitle(f'Prediction Samples — {MODEL_NAMES[model_name]} on {DATASET_NAMES[dataset]}'
                     f'  (Acc: {ckpt["accuracy"]*100:.1f}%)',
                     fontsize=16, fontweight='bold')

        for row in range(3):
            for col in range(10):
                ax = axes[row][col]
                if row < 2:  # 正确预测
                    idx = row * 10 + col
                    if idx < n_correct:
                        img_path, true_id, pred_id, conf = correct_samples[idx]
                        status, tc = 'CORRECT', 'green'
                    else:
                        ax.axis('off'); continue
                else:  # 错误预测
                    idx = col
                    if idx < n_wrong:
                        img_path, true_id, pred_id, conf = wrong_samples[idx]
                        status, tc = 'WRONG', 'red'
                    else:
                        ax.axis('off'); continue

                img = Image.open(img_path).convert('RGB')
                ax.imshow(img)
                true_name = idx_to_class.get(true_id, f'cls_{true_id}')[:18]
                pred_name = idx_to_class.get(pred_id, f'cls_{pred_id}')[:18]
                ax.set_title(f'{status}\nTrue: {true_name}\nPred: {pred_name}\nConf: {conf:.2f}',
                             fontsize=7, color=tc, fontweight='bold')
                ax.axis('off')

        plt.tight_layout()
        path = OUT_DIR / f'predictions_{model_name}_{dataset}.png'
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'    [OK] {path}')


def main():
    print("Generating visualization charts...\n")
    plot_training_curves()
    plot_comparison_bar()
    plot_efficiency_scatter()
    plot_radar()
    plot_summary_table()
    plot_confusion_matrices()
    plot_prediction_samples()
    print(f"\nAll charts saved to: {OUT_DIR}")


if __name__ == '__main__':
    main()
