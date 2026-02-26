# 项目结构说明

## 目录结构

```
lyedu/
├── lyedu-api-python/       # 后端 API（Python，FastAPI）
├── lyedu-admin/            # 管理后台前端（Vue3 + Element Plus）
├── lyedu-pc/               # PC 端学员前端（Vue3 + Element Plus）
├── lyedu-unix/             # 学员端 H5/微信小程序（uni-app x）
├── lyedu-entry/            # 统一入口（可选）
├── docker/                 # Docker 相关
│   └── mysql/
│       └── init.sql        # MySQL 用户/库初始化；表由 Alembic 创建
├── scripts/                # 脚本与配置
│   ├── dev/                # 开发环境一键启动/停止
│   └── docker/             # Docker compose 与 .env
├── docs/                   # 项目文档
├── pkg/                    # 构建产物（如有）
└── README.md
```

## 技术选型说明

### 后端技术栈
- **FastAPI**：异步 Web 框架
- **Python 3.10+**：推荐 3.14.2
- **PyMySQL**：MySQL 连接
- **Redis**：缓存（可选）
- **Alembic**：数据库迁移
- **JWT**：无状态身份认证

### 前端技术栈
- **Vue 3**：渐进式 JavaScript 框架
- **TypeScript**：类型安全的 JavaScript 超集
- **Vite**：下一代前端构建工具
- **Element Plus**：PC 端 UI 组件库（管理后台、PC 端）
- **uni-app x**：学员端 H5/微信小程序
- **Pinia**：Vue 3 状态管理库
- **Vue Router**：Vue 官方路由管理器
- **Axios**：HTTP 客户端

### 数据库与迁移
- **MySQL 8.0+**
- **lyedu-api-python/alembic/**：Alembic 迁移，启动时自动执行 `alembic upgrade head`

## 开发规范

### 命名规范
- 类名：大驼峰命名（PascalCase）
- 函数/变量：小写下划线（snake_case）
- 常量：全大写下划线分隔

### Git 提交规范
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建/工具相关

## 部署说明

### 本地开发
1. 启动 MySQL 和 Redis（可选 Docker：`scripts/docker` 下 `docker compose -f compose-mysql-redis.yml up -d`）
2. 启动 lyedu-api-python：`cd lyedu-api-python && ENV=dev uvicorn main:app --reload --host 0.0.0.0 --port 9700`
3. 启动 lyedu-admin、lyedu-pc 等前端
4. 或使用一键脚本：`.\scripts\dev\start.ps1`

### Docker 部署
仅 MySQL + Redis：`cd scripts/docker && docker compose -f compose-mysql-redis.yml up -d`，API 与前端本地运行。

## 注意事项

1. **完全原创**：本项目所有代码均为原创，不包含任何第三方项目的代码
2. **图标使用**：前端图标使用 Iconify 开源图标库
3. **数据库迁移**：Python 应用启动时自动执行 Alembic 迁移
4. **环境变量**：生产环境请修改 `.env` 或 `~/.lyedu/conf/config.ini` 中的敏感信息
