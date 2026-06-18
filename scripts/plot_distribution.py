"""
生成数据集分布图 — 两个数据集的类别-图片数量柱状图
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / 'data' / 'processed'
OUT = ROOT / 'docs' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)


def plot_dataset_distribution(dataset_key, title, color_map):
    """绘制单个数据集的类别分布图"""
    split_file = PROCESSED / dataset_key / 'split_info.json'
    with open(split_file, 'r', encoding='utf-8') as f:
        info = json.load(f)

    class_counts = info['class_counts']

    # Oxford 102: 用 idx_to_class 找英文名
    if dataset_key == 'oxford102':
        idx_to_class = info.get('idx_to_class', {})
        labeled = {}
        for k, v in class_counts.items():
            name = idx_to_class.get(str(k), f'class_{k}')
            labeled[name] = v
    else:
        labeled = dict(class_counts)

    # 按数量降序排列
    sorted_items = sorted(labeled.items(), key=lambda x: x[1], reverse=True)
    names = [n for n, _ in sorted_items]
    counts = [c for _, c in sorted_items]

    fig, ax = plt.subplots(figsize=(16, 10))

    # 渐变色柱状图
    colors = plt.cm.viridis(np.linspace(0.1, 0.85, len(counts)))
    bars = ax.bar(range(len(counts)), counts, color=colors, width=0.8, edgecolor='white', linewidth=0.3)

    # 标注统计信息
    ax.text(0.98, 0.94, f'类别数: {len(counts)}', transform=ax.transAxes,
            fontsize=13, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='#ddd'))
    ax.text(0.98, 0.87, f'图片总数: {sum(counts)}', transform=ax.transAxes,
            fontsize=13, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='#ddd'))
    ax.text(0.98, 0.80, f'平均每类: {sum(counts)/len(counts):.0f} 张', transform=ax.transAxes,
            fontsize=13, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='#ddd'))
    ax.text(0.98, 0.73, f'最少: {min(counts)} | 最多: {max(counts)}', transform=ax.transAxes,
            fontsize=13, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='#ddd'))

    # 中位线和均值线
    median_val = np.median(counts)
    mean_val = np.mean(counts)
    ax.axhline(y=median_val, color='#e74c3c', linestyle='--', linewidth=1.2, alpha=0.7,
               label=f'中位数: {median_val:.0f}')
    ax.axhline(y=mean_val, color='#f39c12', linestyle=':', linewidth=1.2, alpha=0.7,
               label=f'平均值: {mean_val:.0f}')

    ax.set_xlabel('类别（按数量降序排列）', fontsize=13)
    ax.set_ylabel('图片数量', fontsize=13)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.set_xticks([])
    ax.set_xlim(-0.5, len(counts) - 0.5)
    ax.grid(axis='y', alpha=0.3, linestyle='-')

    plt.tight_layout()
    path = OUT / f'distribution_{dataset_key}.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'已保存: {path}')
    return sum(counts), min(counts), max(counts)


# ── Caltech-101 ──
print('生成 Caltech-101 分布图...')
plot_dataset_distribution('caltech101', 'Caltech-101 类别分布\n（101 类物体识别数据集）', 'Blues')

# ── Oxford 102 ──
print('生成 Oxford 102 分布图...')
plot_dataset_distribution('oxford102', 'Oxford 102 Flower 类别分布\n（102 种花卉细粒度分类数据集）', 'Oranges')

# ── 合并对比图 ──
print('生成合并对比图...')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

for ax, dataset_key, title, cmap in [
    (ax1, 'caltech101', 'Caltech-101', 'Blues'),
    (ax2, 'oxford102', 'Oxford 102 Flower', 'Oranges'),
]:
    split_file = PROCESSED / dataset_key / 'split_info.json'
    with open(split_file, 'r', encoding='utf-8') as f:
        info = json.load(f)

    class_counts = info['class_counts']
    if dataset_key == 'oxford102':
        idx_to_class = info.get('idx_to_class', {})
        labeled = {idx_to_class.get(str(k), f'class_{k}'): v for k, v in class_counts.items()}
    else:
        labeled = dict(class_counts)

    sorted_items = sorted(labeled.items(), key=lambda x: x[1], reverse=True)
    counts = [c for _, c in sorted_items]

    colors = matplotlib.colormaps[cmap](np.linspace(0.2, 0.9, len(counts)))
    ax.bar(range(len(counts)), counts, color=colors, width=0.8, edgecolor='white', linewidth=0.2)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('类别（按数量降序）', fontsize=12)
    ax.set_ylabel('图片数量', fontsize=12)
    ax.set_xticks([])
    ax.axhline(y=np.mean(counts), color='red', linestyle='--', linewidth=1, alpha=0.5,
               label=f'均值: {np.mean(counts):.0f}')
    ax.legend(fontsize=10)

plt.tight_layout()
path = OUT / 'distribution_comparison.png'
fig.savefig(path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f'已保存: {path}')
print('完成！')
