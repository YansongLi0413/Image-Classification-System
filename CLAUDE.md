# Claude Code 项目配置

## 语言要求
- **输出语言**：始终使用简体中文回答，包括代码注释、解释和所有沟通内容。
- **例外**：代码中的变量名、函数名、类名等标识符保持英文；专有名词（如 Flask, PyTorch, ResNet50）可用原文。
- 代码中的变量名、函数名等标识符仍保持英文（符合编程惯例）。

## 项目上下文
- 项目名称：AI_APP（墨瞳 — 图像分类智能应用）
- Python 版本：3.10
- 包管理工具：Conda（环境名：AI_APP）
- 主要技术栈：
  - 深度学习：PyTorch 2.5 + torchvision
  - 后端：Django 4.2 + Django REST Framework 3.14
  - 认证：Simple JWT（Access Token 30min + Refresh Token 7d）
  - 前端：Vue 3.4 + Vite 5.x + Element Plus 2.x
  - 状态管理：Pinia 2.x
  - 路由：Vue Router 4.x
  - HTTP 客户端：Axios 1.x（JWT 自动刷新拦截器）
  - 数据库：SQLite（开发）/ MySQL（生产）
  - 缓存：Redis（可选降级为 LocMem）
- 前端设计系统：**墨韵科技 Ink-Tech**
  - 主色：深邃墨蓝 `#1a2744` | 强调色：暖金 `#c9a96e` | 底色：暖米白 `#faf8f5`
  - 标题字体：思源宋体 (Noto Serif SC) | 正文字体：苹方/微软雅黑
  - 全局主题变量定义在 `frontend/src/styles/theme.css`，覆盖 Element Plus 默认样式
  - 移动端优先响应式：768px / 1024px 断点，导航栏毛玻璃 + 抽屉菜单
- 数据集：data\raw\caltech-101 dataset 和 data\raw\Oxford 102 Flower Dataset
- 五个模型：Custom CNN / ResNet-50 / EfficientNet-B1 / ViT-B/16 / DenseNet-121
- 仓库地址：https://github.com/YansongLi0413/AI_APP
- 每完成一个关键小任务就要进行 git 提交

## 编码规范
- 风格：遵循 PEP 8。
- 类型注解：建议为函数参数和返回值添加类型注解。
- 错误处理：关键操作（文件读取、模型推理）需包含 try-except。
- 日志：使用 Python `logging` 模块，输出级别 INFO 或 DEBUG。

- 所有公共函数必须有文档字符串（docstring），文档字符串用中文写。

## 前端编码规范
- 使用 Vue 3 Composition API（`<script setup>` 语法）
- Element Plus 组件功能保留，通过 CSS 变量覆盖样式
- 响应式设计：移动端优先，使用 `min-width` 媒体查询
- 页面切换统一使用 `<Transition>` 动画
- API 调用统一通过 `src/api/client.js` 的 Axios 实例

## 后端模块结构
```
backend/
├── config/settings/base.py    # 基础配置（数据库/缓存/JWT/CORS/日志）
├── apps/
│   ├── users/       # 用户模块（注册/登录/信息/改密）
│   ├── predictions/ # 预测模块（上传/推理/历史/热门）
│   └── models_manager/ # 模型管理（列表/切换/热更新）
├── services/
│   ├── predict_service.py  # 模型加载缓存 + 推理（_MODEL_CACHE 单例）
│   ├── model_manager.py    # 默认模型切换 + 预加载
│   ├── image_service.py    # 图片保存（SHA256 去重）
│   └── auth_service.py     # JWT Token 生成
├── middleware/    # request_logging + exception_handler
└── utils/         # cache + validators + response
```

## 前端模块结构
```
frontend/src/
├── styles/theme.css   # 全局设计令牌 + Element Plus 变量覆盖
├── views/             # 页面组件
│   ├── Home.vue       # 首页（Hero + 特性 + 模型展示 + CTA）
│   ├── Predict.vue    # 预测页（分段选择器 + 拖拽上传 + 置信度环形图）
│   ├── History.vue    # 历史记录（桌面表格 + 移动卡片双视图）
│   ├── Login.vue      # 登录（左右分栏品牌展示区）
│   ├── Register.vue   # 注册（左右分栏）
│   └── Profile.vue    # 个人中心（用户卡片 + 改密表单）
├── components/        # AppNavbar（毛玻璃导航） + AppFooter（深色三列）
├── stores/auth.js     # Pinia 认证状态（JWT + 用户信息持久化）
├── api/client.js      # Axios 实例（baseURL: /api, JWT 注入 + 自动刷新）
└── router/index.js    # 路由配置 + 导航守卫（requiresAuth）
```

## 交互指令
- 当被问到"解释这段代码"时，用中文逐行说明。
- 提供代码示例时，优先给出可直接运行的完整代码块。
- 若需要安装依赖，先检查是否在 Conda 环境中，再给出安装命令（例如 `conda install` 或 `pip install`）。
- 修改前端样式时，优先使用 `frontend/src/styles/theme.css` 中定义的 CSS 变量，保持设计一致性。

## 项目任务

### 1. 数据集

选定两个数据集，即 data\raw\caltech-101 dataset 和 data\raw\Oxford 102 Flower Dataset

这两个都是图片数据集

完成相应的人工智能任务：
1. 数据清洗、数据预处理步骤（若不需要可忽略）
2. 模型的设计与实现，需要设计五个模型，并且两个数据集跑完五个模型后要进行模型分析，准确率分析，要保证准确率 95% 以上，保底 90%，五个模型要有评估指标，实验结果，对比分析

要求有前端页面跟用户进行交互，用户在前端输入后，后端根据输入进行相应任务的预测，并将预测结果返回给用户。
技术要求：前端页面使用 Vue 开发，后端接口使用 Django
