# API 接口文档

> 基础 URL: `http://127.0.0.1:8000/api`
> 认证方式: JWT Bearer Token
> 内容类型: `application/json`

---

## 1. 认证模块 `/api/auth/`

### 1.1 注册
```
POST /api/auth/register/
Content-Type: application/json

Request:
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456"
}

Response 201:
{
  "user": { "id": 1, "username": "testuser", "email": "test@example.com", ... },
  "tokens": { "access": "eyJ...", "refresh": "eyJ..." }
}
```

### 1.2 登录
```
POST /api/auth/login/

Request:  { "username": "testuser", "password": "123456" }
Response: { "user": {...}, "tokens": { "access": "...", "refresh": "..." } }
Error 401: { "error": "用户名或密码错误" }
```

### 1.3 获取当前用户
```
GET /api/auth/me/
Authorization: Bearer <access_token>

Response: { "id": 1, "username": "testuser", "email": "...", "role": "user", ... }
```

### 1.4 修改密码
```
POST /api/auth/change-password/
Authorization: Bearer <access_token>

Request:  { "old_password": "...", "new_password": "..." }
Response: { "message": "密码修改成功" }
```

### 1.5 刷新 Token
```
POST /api/auth/refresh/

Request:  { "refresh": "<refresh_token>" }
Response: { "access": "...", "refresh": "..." }
```

---

## 2. 预测模块 `/api/`

### 2.1 图片预测
```
POST /api/predict/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Request:
  image: <file>           (必填, JPG/PNG, ≤10MB)
  model: "efficientnet_b1"(可选, 默认 efficientnet_b1)
  dataset: "caltech101"   (可选, 默认 caltech101)

Response 200:
{
  "record_id": 1,
  "predicted_class": "airplanes",
  "predicted_class_id": 0,
  "confidence": 0.9856,
  "top5_results": [
    { "class_id": 0, "confidence": 0.9856 },
    { "class_id": 5, "confidence": 0.0123 },
    ...
  ],
  "inference_time_ms": 18.5,
  "image_url": "/storage/images/original/abc.jpg",
  "from_cache": false
}

Error 400: { "error": "图片大小不能超过 10MB" }
Error 500: { "error": "服务器内部错误" }
```

### 2.2 预测历史
```
GET /api/history/?page=1&page_size=20&model=

Authorization: Bearer <access_token>

Response:
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "records": [
    {
      "id": 1,
      "image": { "id": 1, "original_path": "...", "width": 300, "height": 200 },
      "model_name": "efficientnet_b1",
      "dataset_name": "caltech101",
      "predicted_class": "airplanes",
      "confidence": 0.9856,
      "top5_results": [...],
      "inference_time_ms": 18.5,
      "created_at": "2026-06-05T12:00:00Z"
    }
  ]
}
```

### 2.3 预测详情
```
GET /api/history/<id>/

Response: { 单条 PredictionRecord }
Error 404: { "error": "记录不存在" }
```

### 2.4 热门预测
```
GET /api/history/hot/

Response:
{
  "hot_predictions": [
    { "predicted_class": "sunflower", "count": 45 },
    ...
  ]
}
```

---

## 3. 模型管理 `/api/models/`

### 3.1 模型列表
```
GET /api/models/
Authorization: Bearer <access_token>

Response:
{
  "models": [
    { "name": "efficientnet_b1", "display_name": "EfficientNet-B1",
      "dataset_name": "caltech101", "accuracy": 0.93, "file_size_mb": 25.8 },
    ...
  ]
}
```

### 3.2 切换默认模型
```
POST /api/models/switch/
Authorization: Bearer <access_token>

Request:  { "model": "densenet121" }
Response: { "message": "默认模型已切换为 densenet121", "model": "densenet121" }
```

### 3.3 模型热更新
```
POST /api/models/reload/
Authorization: Bearer <access_token>

Request:  { "model": "efficientnet_b1" }
Response: { "message": "模型 efficientnet_b1 热更新完成" }
Error 500: { "error": "模型文件不存在" }
```

---

## 4. 通用错误码

| 状态码 | 说明 |
|:---:|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 / Token 过期 |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

错误响应格式:
```json
{
  "error": true,
  "code": 400,
  "detail": "具体错误信息",
  "path": "/api/predict/"
}
```

## 5. 速率限制

| 接口 | 限制 |
|------|------|
| 所有认证接口 | 60次/分钟/用户 |
| 所有匿名接口 | 10次/分钟/IP |
| 登录接口 | 5次/分钟/IP |

## 6. 启动说明

```bash
# 后端
cd backend
python manage.py runserver 0.0.0.0:8000

# 前端
cd frontend
npm run dev
```

访问 `http://localhost:5173` 使用前端界面。
