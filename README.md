# Image-Classification-System — 图像分类智能应用

> **GitHub**: https://github.com/YansongLi0413/Image-Classification-System

基于深度学习的图像分类系统，支持 Caltech-101 和 Oxford 102 Flower 两个数据集。

## 项目概览

```
┌──────────────────────────────────────────────────────────┐
│                    墨瞳 AI_APP                              │
│                                                          │
│  前端: Vue 3 + Element Plus    后端: Django + DRF         │
│  设计: 墨韵科技 Ink-Tech         模型: PyTorch 2.x          │
│  字体: 思源宋体 + 苹方             缓存: Redis / LocMem      │
└──────────────────────────────────────────────────────────┘
```

## 项目结构

```
AI_APP/
├── backend/                  # Django 后端 API
│   ├── config/               # Django 配置 (base/dev)
│   ├── apps/                 # 应用模块
│   │   ├── users/            # 用户模块（注册/登录/JWT）
│   │   ├── predictions/      # 预测模块（图片上传/推理/历史）
│   │   └── models_manager/   # 模型管理（列表/切换/热更新）
│   ├── services/             # 服务层
│   │   ├── predict_service.py  # 模型加载缓存 + 推理
│   │   ├── model_manager.py    # 模型生命周期管理
│   │   ├── image_service.py    # 图片存储（SHA256 去重）
│   │   └── auth_service.py     # JWT Token 生成
│   ├── middleware/           # 请求日志 + 异常处理
│   └── utils/               # 缓存 / 校验 / 响应格式化
├── frontend/                 # Vue 3 前端
│   └── src/
│       ├── styles/           # 全局主题系统 (theme.css)
│       ├── views/            # 页面（首页/预测/历史/登录/注册/个人中心）
│       ├── components/       # 公共组件（导航栏/页脚）
│       ├── stores/           # Pinia 状态管理（auth）
│       ├── api/              # Axios HTTP 客户端（JWT 自动刷新）
│       └── router/           # Vue Router（路由守卫）
├── models/                   # 模型定义与训练
│   ├── custom_cnn.py         # 自定义 5 层 CNN
│   ├── resnet50.py           # ResNet-50（迁移学习）
│   ├── efficientnet.py       # EfficientNet-B1（迁移学习）
│   ├── vit.py                # ViT-B/16（迁移学习）
│   ├── densenet.py           # DenseNet-121（迁移学习）
│   ├── dataset.py            # PyTorch Dataset 类
│   ├── trainer.py            # 统一训练器（两阶段训练）
│   ├── train.py              # 训练入口脚本
│   ├── evaluate.py           # 测试集评估脚本
│   └── visualize.py          # 可视化脚本
├── scripts/
│   └── preprocess.py         # 数据预处理（划分/统计）
├── data/
│   ├── raw/                  # 原始数据集（不跟踪）
│   └── processed/            # 预处理后数据（不跟踪）
├── saved_models/             # 训练好的模型权重（不跟踪）
├── notebooks/                # Jupyter 分析笔记
├── docs/                     # 项目文档
│   ├── architecture.md       # 系统架构设计
│   ├── api_spec.md           # API 接口文档
│   ├── data_analysis_and_preprocessing.md
│   └── model_design_and_training_log.md
├── storage/                  # 用户上传文件 & 日志（不跟踪）
├── requirements.txt          # Python 依赖
```

## 数据集

| 数据集 | 类别数 | 图片数 | 来源 |
|--------|--------|--------|------|
| Caltech-101 | 101 类 | 9,144 | Caltech |
| Oxford 102 Flower | 102 类 | 8,189 | Oxford VGG |

## 五大模型

| # | 模型 | 类型 | 骨干网络 | 参数量 | Caltech-101 准确率 | Oxford 102 准确率 |
|---|------|------|----------|--------|-------------------|-------------------|
| 1 | **Custom CNN** | 从头训练 | 5 层卷积 + 2 层 FC | ~25M | ≥ 90% | ≥ 90% |
| 2 | **ResNet-50** | 迁移学习 | ResNet-50 (ImageNet) | ~25M | ≥ 93% | ≥ 93% |
| 3 | **EfficientNet-B1** | 迁移学习 | EfficientNet-B1 (ImageNet) | ~7.8M | ≥ 95% | ≥ 95% |
| 4 | **ViT-B/16** | 迁移学习 | Vision Transformer (ImageNet-21k) | ~86M | ≥ 92% | ≥ 92% |
| 5 | **DenseNet-121** | 迁移学习 | DenseNet-121 (ImageNet) | ~8M | ≥ 95% | ≥ 95% |

### 训练策略

- **迁移学习模型**：两阶段训练
  - 阶段一：冻结骨干，训练分类头（15 epochs, lr=0.001）
  - 阶段二：解冻骨干，全网络微调（35 epochs, lr=0.0001）
- **自定义 CNN**：从头训练 50 epochs
- **Caltech-101 优化**：类别权重 + 标签平滑(0.1) + RandAugment + RandomErasing
- **优化器**：AdamW + CosineAnnealingLR
- **早停**：5-10 epochs 无改善自动停止

### 评估指标

- Top-1 / Top-5 Accuracy
- Precision / Recall / F1 Score (Macro)
- 推理时间 (ms) — 100 次预热 + 100 次推理取平均
- 模型大小 (MB)
- 混淆矩阵 + 训练曲线可视化

## 前端设计系统

### 设计方向：墨韵科技 (Ink-Tech)

| 元素 | 说明 |
|------|------|
| **主色调** | 深邃墨蓝 `#1a2744` — 沉稳专业 |
| **强调色** | 暖金 `#c9a96e` — 精致点缀 |
| **底色** | 暖米白 `#faf8f5` — 温润舒适 |
| **标题字体** | 思源宋体 (Noto Serif SC) — 东方韵味 |
| **正文字体** | 苹方 / 微软雅黑 — 中文阅读优化 |
| **圆角** | 10-16px 大圆角 — 柔和现代 |
| **阴影** | 多层精致阴影 — 深度层次感 |

### 页面功能

| 页面 | 路由 | 功能 | 权限 |
|------|------|------|------|
| 首页 | `/` | Hero 品牌展示 + 特性卡片 + 模型环形图 + CTA | 公开 |
| 图片预测 | `/predict` | 数据集/模型选择 + 拖拽上传 + Top-5 结果 | 需登录 |
| 历史记录 | `/history` | 预测记录表格/卡片 + 模型筛选 + 分页 | 需登录 |
| 个人中心 | `/profile` | 用户信息 + 预测次数 + 修改密码 | 需登录 |
| 登录 | `/login` | 左右分栏布局 + JWT 认证 | 公开 |
| 注册 | `/register` | 左右分栏布局 + 表单校验 | 公开 |

### 响应式设计

| 断点 | 宽度 | 适配 |
|------|------|------|
| 手机 | < 768px | 导航变抽屉菜单 + 表格变卡片 + 单列布局 |
| 平板 | 768px - 1023px | 双列网格 + 导航链接显示 |
| 桌面 | ≥ 1024px | 完整布局 + 多列网格 + 悬停动效 |

## 后端技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 框架 | Django 4.2 + DRF 3.14 | REST API 后端 |
| 认证 | Simple JWT | Access Token(30min) + Refresh Token(7d) |
| 数据库 | SQLite (开发) / MySQL (生产) | Django ORM |
| 缓存 | Redis / LocMem | 预测结果缓存 1h |
| 文件存储 | 本地 storage/ 目录 | 图片 SHA256 去重 |
| 限流 | DRF Throttling | 认证 60次/分, 匿名 10次/分 |
| 中间件 | CORS + 请求日志 + 异常处理 | — |
| 日志 | RotatingFileHandler | 30 天保留，按天轮转 |

## API 端点一览

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register/` | 用户注册 | 否 |
| POST | `/api/auth/login/` | 用户登录 | 否 |
| GET | `/api/auth/me/` | 获取当前用户信息（含 predictions_count） | 是 |
| POST | `/api/auth/change-password/` | 修改密码 | 是 |
| POST | `/api/auth/refresh/` | 刷新 JWT Token | 否 |
| POST | `/api/predict/` | 上传图片执行预测 | 是 |
| GET | `/api/history/` | 预测历史（分页+筛选） | 是 |
| GET | `/api/history/<id>/` | 预测详情 | 是 |
| GET | `/api/history/hot/` | 热门预测 Top-N | 是 |
| GET | `/api/models/` | 可用模型列表 | 是 |
| POST | `/api/models/switch/` | 切换默认模型 | 是 |
| POST | `/api/models/reload/` | 模型热更新 | 是 |

详细请求/响应格式见 [docs/api_spec.md](docs/api_spec.md)。

## 快速开始

```bash
# 1. 创建 Conda 环境
conda create -n AI_APP python=3.10
conda activate AI_APP

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据预处理（生成划分文件 + 统计信息）
python scripts/preprocess.py

# 4. 训练模型（示例：EfficientNet-B1 on Caltech-101）
python models/train.py --model efficientnet_b1 --dataset caltech101

# 5. 评估模型
python models/evaluate.py --model all --dataset all

# 6. 启动后端（端口 8000）
cd backend && python manage.py runserver

# 7. 启动前端（端口 5173，自动代理到后端）
cd frontend && npm install && npm run dev
```

访问 `http://localhost:5173` 使用前端界面。

## 相关文档

- [系统架构设计](docs/architecture.md)
- [API 接口文档](docs/api_spec.md)
- [数据分析与预处理](docs/data_analysis_and_preprocessing.md)
- [模型设计与训练日志](docs/model_design_and_training_log.md)
