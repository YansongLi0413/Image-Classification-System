"""
生成数据集分布图 — 水平柱状图 + 各类别名称标注
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / 'data' / 'processed'
OUT = ROOT / 'docs' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)


def load_sorted(dataset_key):
    """加载并按数量降序排列"""
    split_file = PROCESSED / dataset_key / 'split_info.json'
    with open(split_file, 'r', encoding='utf-8') as f:
        info = json.load(f)

    class_counts = info['class_counts']
    if dataset_key == 'oxford102':
        idx_to_class = info.get('idx_to_class', {})
        labeled = {idx_to_class.get(str(k), f'class_{k}'): v
                   for k, v in class_counts.items()}
    else:
        labeled = dict(class_counts)

    items = sorted(labeled.items(), key=lambda x: x[1], reverse=True)
    return [n for n, _ in items], [c for _, c in items]


def plot_horizontal(dataset_key, title, colormap_name):
    """水平柱状图 — 每根柱子旁边标注类别名"""
    names, counts = load_sorted(dataset_key)
    n = len(names)
    total = sum(counts)
    mean_val = np.mean(counts)
    median_val = np.median(counts)

    # 柱高 = 类别数 / 6 英寸，确保标签不重叠
    fig_height = max(10, n * 0.22)
    fig, ax = plt.subplots(figsize=(12, fig_height))

    colors = matplotlib.colormaps[colormap_name](np.linspace(0, 1.0, n))
    y_pos = range(n)

    bars = ax.barh(y_pos, counts, height=0.75, color=colors, edgecolor='white', linewidth=0.3)

    # 每条柱子上标注数量
    for i, (name, cnt) in enumerate(zip(names, counts)):
        ax.text(cnt + max(counts) * 0.01, i, f'{cnt}',
                va='center', fontsize=6, color='#555')

    # Y轴标签 = 类别名
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=5.5, va='center')
    # 奇数位灰色，偶数位深色（增强可读）
    for i, label in enumerate(ax.get_yticklabels()):
        label.set_color('#444' if i % 2 == 0 else '#777')

    # 中位数和均值竖线
    ax.axvline(x=mean_val, color='#f39c12', linestyle=':', linewidth=1.5, alpha=0.8,
               label=f'平均值: {mean_val:.0f}')
    ax.axvline(x=median_val, color='#e74c3c', linestyle='--', linewidth=1.2, alpha=0.7,
               label=f'中位数: {median_val:.0f}')

    # 统计信息框 — 放在右下角图内，避免与标题重叠
    stats_text = (f'类别数: {n}    图片总数: {total}\n'
                  f'平均/类: {mean_val:.0f}    中位数: {median_val:.0f}\n'
                  f'最少: {min(counts)}    最多: {max(counts)}')
    ax.text(0.97, 0.03, stats_text, transform=ax.transAxes, fontsize=9,
            ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='white', alpha=0.92,
                      edgecolor='#ccc', linewidth=0.8))

    ax.set_xlabel('图片数量', fontsize=13)
    ax.set_title(title, fontsize=15, fontweight='bold', pad=12)
    ax.legend(loc='lower left', fontsize=10, framealpha=0.9)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.25, linestyle='-')
    ax.set_xlim(0, max(counts) * 1.18)

    plt.tight_layout()
    path = OUT / f'distribution_{dataset_key}.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'已保存: {path}')


def plot_comparison():
    """并排对比 — 抽样式标注"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    for ax, key, title, cmap in [
        (ax1, 'caltech101', 'Caltech-101', 'Blues'),
        (ax2, 'oxford102', 'Oxford 102 Flower', 'Oranges'),
    ]:
        names, counts = load_sorted(key)
        n = len(counts)
        colors = matplotlib.colormaps[cmap](np.linspace(0, 1.0, n))

        ax.bar(range(n), counts, color=colors, width=0.85, edgecolor='white', linewidth=0.2)

        # 每隔 N 个标注一个类别名（避免拥挤）
        step = max(1, n // 18)
        for i in range(0, n, step):
            ax.text(i, counts[i] + max(counts) * 0.02, names[i],
                    ha='center', va='bottom', fontsize=6.5, rotation=90, color='#444')

        # 前5名必须标注
        for i in range(5):
            ax.text(i, counts[i] + max(counts) * 0.02, names[i],
                    ha='center', va='bottom', fontsize=7, rotation=90,
                    color='#222', fontweight='bold')

        ax.set_title(title, fontsize=14, fontweight='bold')
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


# ── 主程序 ──
print('生成 Caltech-101 水平分布图（含各类别名）...')
plot_horizontal('caltech101', 'Caltech-101 类别分布（101 类物体识别数据集）', 'Blues')

print('生成 Oxford 102 水平分布图（含各类别名）...')
plot_horizontal('oxford102', 'Oxford 102 Flower 类别分布（102 种花卉细粒度分类数据集）', 'Oranges')

print('生成合并对比图（采样标注）...')
plot_comparison()

print('完成！')
