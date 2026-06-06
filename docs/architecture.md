# 系统架构设计文档

> AI_APP — 图像分类智能应用
> 版本: 1.0 | 日期: 2026-06-05

---

## 1. 整体架构

```
┌──────────────────────────────────────────────────────┐
│                    Presentation Layer                 │
│  ┌─────────────────────┐  ┌───────────────────────┐  │
│  │   Vue 3 + Vite       │  │   Mobile Browser      │  │
│  │   (PC Desktop)       │  │   (Responsive)        │  │
│  └──────────┬──────────┘  └───────────┬───────────┘  │
└─────────────┼──────────────────────────┼──────────────┘
              │       HTTPS/REST API     │
┌─────────────┼──────────────────────────┼──────────────┐
│             ▼                          ▼              │
│               Django REST Framework (Backend)          │
│  ┌──────────────────────────────────────────────────┐ │
│  │               Middleware Layer                    │ │
│  │  JWT Auth │ CORS │ Rate Limit │ Request Logging  │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │ Auth API │ │ Predict  │ │ History / User Mgmt  │ │
│  │ (JWT)    │ │ API      │ │ API                  │ │
│  └────┬─────┘ └────┬─────┘ └──────────┬───────────┘ │
│       │             │                  │              │
│  ┌────┴─────────────┴──────────────────┴───────────┐ │
│  │                Service Layer                     │ │
│  │  AuthService │ PredictService │ HistoryService   │ │
│  │  ModelManager (热更新) │ ImageProcessor          │ │
│  └──────────────────────┬──────────────────────────┘ │
│                         │                             │
│  ┌──────────────────────┼──────────────────────────┐ │
│  │            Data Access Layer (DAL)               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │ │
│  │  │ MySQL    │  │ Redis    │  │ File Storage  │  │ │
│  │  │ (主数据库) │  │ (缓存)    │  │ (图片/模型)    │  │ │
│  │  └──────────┘  └──────────┘  └───────────────┘  │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 2. 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + Vite | 3.x / 5.x |
| UI 组件库 | Element Plus | 2.x |
| 路由 | Vue Router | 4.x |
| 状态管理 | Pinia | 2.x |
| HTTP 客户端 | Axios | 1.x |
| 设计系统 | 墨韵科技 Ink-Tech | — |
| 标题字体 | 思源宋体 (Noto Serif SC) | — |
| 正文字体 | 苹方 / 微软雅黑 | — |
| 后端框架 | Django + DRF | 4.2 / 3.14 |
| 认证 | Simple JWT | 5.x |
| 数据库 | SQLite (开发) / MySQL (生产) | 8.x |
| 缓存 | Redis + django-redis (可选降级为 LocMem) | 7.x |
| 日志 | Python logging + RotatingFileHandler | — |
| 部署 | Gunicorn + Nginx (生产) | — |

### 2.1 前端设计令牌

| 令牌类别 | 变量前缀 | 说明 |
|----------|----------|------|
| 主色系 | `--ink-*` | 墨蓝 900-50 色阶 |
| 强调色系 | `--gold-*` | 暖金 900-50 色阶 |
| 中性色系 | `--warm-*` | 暖调灰 900-50 色阶 |
| 字体 | `--font-display` / `--font-body` | 思源宋体 / 系统无衬线 |
| 间距 | `--space-*` | 基于 4px 网格 (1-32) |
| 阴影 | `--shadow-*` | xs/sm/md/lg/xl + ink/gold |
| 圆角 | `--radius-*` | xs(4px) → 2xl(28px) |
| 动画 | `--ease-*` / `--duration-*` | expo/quart/spring + fast/normal/slow |

主题文件：`frontend/src/styles/theme.css`（同时覆盖 Element Plus CSS 变量）

## 3. 目录结构

```
AI_APP/
├── backend/
│   ├── manage.py
│   ├── config/                  # Django 配置
│   │   ├── settings/
│   │   │   ├── base.py          # 基础配置
│   │   │   ├── dev.py           # 开发环境
│   │   │   └── prod.py          # 生产环境
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/               # 用户模块
│   │   │   ├── models.py        # User, UserProfile
│   │   │   ├── views.py         # Register, Login, Profile
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   ├── predictions/         # 预测模块
│   │   │   ├── models.py        # PredictionRecord, ImageInfo
│   │   │   ├── views.py         # Predict, History
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   └── models_manager/      # 模型管理
│   │       ├── models.py        # ModelInfo
│   │       ├── views.py         # Model list, switch
│   │       └── urls.py
│   ├── services/                # Service Layer
│   │   ├── auth_service.py
│   │   ├── predict_service.py
│   │   ├── model_manager.py     # 模型热更新
│   │   └── image_service.py
│   ├── middleware/
│   │   ├── request_logging.py
│   │   └── exception_handler.py
│   └── utils/
│       ├── cache.py             # Redis 缓存工具
│       ├── validators.py        # 数据校验
│       └── response.py          # 统一响应格式
├── frontend/
│   ├── src/
│   │   ├── views/               # 页面
│   │   ├── components/          # 组件
│   │   ├── stores/              # Pinia 状态
│   │   ├── api/                 # API 调用
│   │   ├── router/              # 路由
│   │   └── utils/               # 工具函数
│   └── vite.config.js
├── storage/                     # 文件存储
│   ├── images/original/         # 原始上传图片
│   ├── images/processed/        # 处理后图片
│   ├── models/                  # 模型权重文件
│   └── logs/                    # 日志文件
├── docs/
│   ├── architecture.md          # 本文档
│   ├── api_spec.md              # API 接口文档
│   └── database_schema.md       # 数据库设计
└── requirements.txt
```

## 4. 数据库设计

### 4.1 用户表 (users_user)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| username | VARCHAR(150) UNIQUE | 用户名 |
| email | VARCHAR(254) UNIQUE | 邮箱 |
| password | VARCHAR(128) | 密码哈希 |
| avatar | VARCHAR(500) | 头像 URL |
| role | ENUM('user','admin') | 角色 |
| is_active | BOOLEAN | 是否激活 |
| created_at | DATETIME | 创建时间 |
| last_login | DATETIME | 最后登录 |

### 4.2 图片信息表 (predictions_image)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| user_id | FK → users | 上传用户 |
| original_path | VARCHAR(500) | 原始图片路径 |
| processed_path | VARCHAR(500) | 处理后图片路径 |
| original_size | INT | 原始文件大小(bytes) |
| width | INT | 图片宽度 |
| height | INT | 图片高度 |
| format | VARCHAR(10) | 格式(jpg/png) |
| upload_at | DATETIME | 上传时间 |

### 4.3 预测记录表 (predictions_predictionrecord)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| user_id | FK → users | 用户 |
| image_id | FK → images | 关联图片 |
| model_name | VARCHAR(50) | 使用的模型 |
| dataset_name | VARCHAR(50) | 数据集 |
| predicted_class | VARCHAR(100) | 预测类别名 |
| predicted_class_id | INT | 预测类别 ID |
| confidence | FLOAT | 置信度 |
| top5_results | JSON | Top-5 预测结果 |
| is_correct | BOOLEAN | 是否正确(用户反馈) |
| inference_time_ms | FLOAT | 推理耗时 |
| created_at | DATETIME | 预测时间 |

### 4.4 模型信息表 (models_manager_modelinfo)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 主键 |
| name | VARCHAR(50) UNIQUE | 模型标识名 |
| display_name | VARCHAR(100) | 显示名称 |
| dataset_name | VARCHAR(50) | 训练数据集 |
| accuracy | FLOAT | 准确率 |
| file_path | VARCHAR(500) | 模型文件路径 |
| file_size_mb | FLOAT | 模型大小 |
| is_active | BOOLEAN | 是否激活 |
| updated_at | DATETIME | 更新时间 |

## 5. 缓存策略

| 缓存 Key | 类型 | TTL | 说明 |
|----------|------|-----|------|
| `session:{token}` | String | 24h | 用户会话 |
| `predict:{image_hash}:{model}` | String | 1h | 预测结果缓存 |
| `hot_records:daily` | Sorted Set | 24h | 热门预测 Top-N |
| `model:list` | String | 5min | 模型列表 |
| `user:{id}:history` | List | 1h | 用户历史(首页) |

## 6. 存储层

| 目录 | 用途 | 备份策略 |
|------|------|----------|
| `storage/images/original/` | 用户上传原始图 | 不备份(可重新上传) |
| `storage/images/processed/` | 缩略图/处理后图 | 不备份(可重新生成) |
| `storage/models/` | 模型权重文件 | Git LFS 或独立备份 |
| `storage/logs/` | 应用日志 | 按天轮转, 保留30天 |

## 7. 安全设计

| 措施 | 实现 |
|------|------|
| JWT 认证 | access_token(30min) + refresh_token(7d) |
| 文件校验 | 仅允许 jpg/jpeg/png, 最大 10MB, 魔数检测 |
| 速率限制 | 预测 API: 60次/分钟(用户), 登录: 5次/分钟(IP) |
| SQL 注入防护 | Django ORM 参数化查询 |
| XSS 防护 | Vue 默认转义 + CSP Header |
| CORS | 白名单模式(生产环境) |

## 8. 模型热更新

```
1. 上传新模型权重 → storage/models/
2. POST /api/models/reload → ModelManager.reload()
3. 新请求使用新模型, 旧请求不受影响(引用计数)
4. 记录热更新日志
```

## 9. 部署架构

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  Nginx   │────▶│  Gunicorn    │────▶│  Django  │
│  (静态文件) │     │  (WSGI, 4 workers) │  │  (App)   │
└──────────┘     └──────────────┘     └──────────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                         ┌────────┐   ┌──────────┐   ┌──────────┐
                         │ MySQL  │   │  Redis   │   │  Celery  │
                         │ (主库)  │   │ (缓存)    │   │ (异步任务) │
                         └────────┘   └──────────┘   └──────────┘
```
