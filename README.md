# Video Slicer API

热门视频切片生产级工具 API，基于 FastAPI + Celery 构建。

## 功能特性

- 视频上传与管理
- 自动视频切片（固定时长或场景检测）
- AI 内容生成（基于 Ollama）
- 异步任务处理
- RESTful API

## 技术栈

- **后端**: FastAPI
- **任务队列**: Celery + Redis
- **数据库**: SQLite
- **AI**: Ollama
- **视频处理**: FFmpeg

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd video_slicer_python
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改：

```bash
cp .env.example .env
```

主要配置项：
- `REDIS_URL`: Redis 连接地址（默认 `redis://localhost:6379/0`）
- `DATABASE_URL`: 数据库连接地址
- `OLLAMA_URL`: Ollama 服务地址
- `OLLAMA_MODEL`: 使用的 AI 模型

### 5. 启动服务

#### 启动 Redis（需要先安装）

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
```

#### 启动 FastAPI 服务

```bash
CELERY_BROKER_URL=redis://localhost:6379/0 .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 启动 Celery Worker

```bash
CELERY_BROKER_URL=redis://localhost:6379/0 .venv/bin/celery -A celery_app.app worker -n worker1@%h --loglevel=info
```

### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/health

## API 接口

### 认证

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/register | 用户注册 |

### 视频

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/videos | 上传视频 |
| GET | /api/videos | 获取视频列表 |
| GET | /api/videos/{video_id} | 获取视频详情 |

### 切片

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/slices | 创建切片 |
| GET | /api/slices | 获取切片列表 |
| GET | /api/slices/{slice_id} | 获取切片详情 |

### 任务

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/tasks/{task_id} | 获取任务状态 |

## 测试账号

默认测试用户：
- 用户名: `test123`
- 密码: `password`

## 项目结构

```
video_slicer_python/
├── api/                    # API 层
│   ├── routes/            # 路由定义
│   ├── schemas/           # Pydantic 模型
│   └── dependencies.py    # 依赖注入
├── celery_app/            # Celery 配置
│   ├── app.py            # Celery 应用
│   └── tasks/            # 任务定义
├── config/                # 配置
├── domain/                # 领域层
│   ├── entities/         # 实体
│   └── services/         # 领域服务
├── infrastructure/        # 基础设施层
│   ├── database/         # 数据库
│   ├── services/        # 外部服务
│   └── storage/         # 文件存储
├── uploads/              # 上传文件目录
├── main.py               # 应用入口
└── requirements.txt      # 依赖列表
```

## 开发

### 运行测试

```bash
pytest
```

### 代码格式

```bash
# 如需格式化工具可自行添加
ruff check .
ruff format .
```

## 生产环境部署

1. 修改 `.env` 中的 `DEBUG=False`
2. 设置安全的 `SECRET_KEY`
3. 配置 CORS 白名单
4. 使用 Nginx 反向代理
5. 使用 Gunicorn 替代 uvicorn

示例生产启动命令：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 许可证

MIT License