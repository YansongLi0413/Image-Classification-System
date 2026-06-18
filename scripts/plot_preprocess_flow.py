"""
生成数据预处理与增强流程图 (图2-1)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(16, 9))
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis('off')

# 配色
INK = '#1a2744'
GOLD = '#c9a96e'
BLUE = '#2a4a8a'
GREEN = '#388e56'
ORANGE = '#e67e22'
GRAY = '#7f8c8d'
BG = '#faf8f5'
WHITE = '#ffffff'

fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)


def draw_box(x, y, w, h, text, color=BLUE, fontsize=11, bold=True, subtitle=''):
    """绘制圆角矩形框"""
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle='round,pad=0.15', facecolor=color, edgecolor='white',
                         linewidth=2, alpha=0.92, zorder=3)
    ax.add_patch(box)
    ax.text(x, y + 0.08 if subtitle else y, text, ha='center', va='center',
            fontsize=fontsize, fontweight='bold' if bold else 'normal',
            color='white', zorder=4)
    if subtitle:
        ax.text(x, y - 0.22, subtitle, ha='center', va='center',
                fontsize=8, fontweight='normal', color='#cccccc', zorder=4)


def draw_arrow(x1, y1, x2, y2, color=GRAY, lw=1.5):
    """绘制箭头"""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                connectionstyle='arc3,rad=0'))


def draw_label(x, y, text, color=GRAY, fontsize=9):
    """绘制标签文字"""
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, color=color,
            fontweight='normal')


# ═══════════════════════════════════════════════════════
# 标题
# ═══════════════════════════════════════════════════════
ax.text(8, 8.5, '数据预处理与增强流程图', ha='center', va='center',
        fontsize=20, fontweight='bold', color=INK)
ax.text(8, 8.05, 'Data Preprocessing & Augmentation Pipeline', ha='center', va='center',
        fontsize=11, color=GOLD, style='italic')

# ═══════════════════════════════════════════════════════
# 第一行：数据清洗阶段
# ═══════════════════════════════════════════════════════
y1 = 6.8
draw_box(3, y1, 3.2, 0.9, '原始数据集', BLUE, 12,
         subtitle='Caltech-101 + Oxford 102')

draw_arrow(4.7, y1, 6.3, y1)

draw_box(7.5, y1, 2.8, 0.9, '数据清洗', GRAY, 12,
         subtitle='文件验证 · 格式统一 · 重命名')

draw_arrow(9.0, y1, 10.6, y1)

draw_box(12, y1, 3.0, 0.9, '标签映射构建', GREEN, 12,
         subtitle='class_to_idx / idx_to_class')

# 第二行：数据划分
y2 = 5.3
draw_arrow(12, 6.3, 12, 5.85, GRAY)

draw_box(12, 5.3, 3.0, 0.8, '分层划分 70/15/15', GOLD, 12,
         subtitle='Stratified Split (seed=42)')

# 分支到三个子集
y3 = 3.8
for bx, label in [(5, '训练集 Train\n70% · ~6,400张'), (12, '验证集 Val\n15% · ~1,400张'), (19, '测试集 Test\n15% · ~1,400张')]:
    # Arrow from center to each branch... simplified
    pass

# 用三列展示
draw_arrow(12, 4.85, 5, 4.3, GRAY)
draw_arrow(12, 4.85, 12, 4.3, GRAY)
draw_arrow(12, 4.85, 19, 4.3, GRAY)  # not needed

# Three columns for the three splits
y3 = 3.9
draw_box(3.5, y3, 3.0, 0.8, '训练集 (Train)', BLUE, 11, subtitle='70% · ~6,400张')
draw_box(8.0, y3, 3.0, 0.8, '验证集 (Val)', BLUE, 11, subtitle='15% · ~1,400张')
draw_box(12.5, y3, 3.0, 0.8, '测试集 (Test)', BLUE, 11, subtitle='15% · ~1,400张')

# ═══════════════════════════════════════════════════════
# 第三行：通用预处理
# ═══════════════════════════════════════════════════════
y4 = 2.5
# Arrows from three boxes down
for bx in [3.5, 8.0, 12.5]:
    draw_arrow(bx, 3.45, 8, 3.05, GRAY)

draw_box(8, 2.5, 6.5, 0.85, '通用图像预处理', BLUE, 12,
         subtitle='Resize(256) → CenterCrop(224) → ToTensor → Normalize(ImageNet)')

# ═══════════════════════════════════════════════════════
# 第四行：训练集专属增强
# ═══════════════════════════════════════════════════════
y5 = 1.1
draw_arrow(8, 2.05, 8, 1.6, GREEN)

draw_box(8, 1.1, 8.5, 0.85, '训练集专属数据增强', GREEN, 12,
         subtitle='RandomCrop · Flip · Rotation · ColorJitter · RandAugment · RandomErasing')

# ═══════════════════════════════════════════════════════
# 标签说明
# ═══════════════════════════════════════════════════════
# 左侧：Caltech-101 增强说明
ax.text(0.5, 1.1, 'Caltech-101 额外增强:', fontsize=8, color=ORANGE, fontweight='bold')
ax.text(0.5, 0.85, 'RandAugment (ops=2, mag=9)\nRandomErasing (p=0.3)', fontsize=7.5, color=GRAY)

# ═══════════════════════════════════════════════════════
# 底部说明
# ═══════════════════════════════════════════════════════
ax.text(8, 0.15, '训练/验证集经预处理后输入 PyTorch DataLoader · 测试集仅做通用预处理', ha='center',
        fontsize=9, color=GRAY, style='italic')

plt.tight_layout()
import os
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'figures')
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, 'preprocessing_flow.png')
fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close(fig)
print(f'已保存: {path}')
