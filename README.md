# AI_APP — 图像分类智能应用

基于深度学习的图像分类系统，支持 Caltech-101 和 Oxford 102 Flower 两个数据集。

## 项目结构

```
AI_APP/
├── backend/                  # Django 后端 API
│   ├── config/               # Django 配置
│   └── api/                  # REST API 应用
├── frontend/                 # Vue 前端
├── data/
│   ├── raw/                  # 原始数据集（不跟踪）
│   └── processed/            # 预处理后数据（不跟踪）
├── scripts/                  # 数据处理脚本
├── models/                   # 模型定义与训练
├── notebooks/                # Jupyter 分析笔记
├── saved_models/             # 训练好的模型权重（不跟踪）
└── requirements.txt          # Python 依赖
```

## 数据集

| 数据集 | 类别数 | 图片数 | 来源 |
|--------|--------|--------|------|
| Caltech-101 | 102 | 9,144 | Caltech |
| Oxford 102 Flower | 102 | 8,189 | Oxford VGG |

## 五个模型

1. **Custom CNN** — 自定义卷积神经网络
2. **ResNet-50** — 残差网络（迁移学习）
3. **EfficientNet-B1** — 高效网络（迁移学习）
4. **Vision Transformer (ViT)** — 视觉Transformer（迁移学习）
5. **DenseNet-121** — 密集连接网络（迁移学习）

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 数据预处理
python scripts/preprocess.py

# 训练模型
python models/train.py --model resnet50 --dataset caltech101

# 启动后端
cd backend && python manage.py runserver

# 启动前端
cd frontend && npm run dev
```
