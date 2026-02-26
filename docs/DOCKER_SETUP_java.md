# Docker 部署指南（Java 版，lyedu-api 已暂停维护）

> **说明**：lyedu-api（Java 后端）已暂停维护，本文档仅供历史参考。当前推荐使用 lyedu-api-python + compose-mysql-redis，详见 [DOCKER_SETUP.md](DOCKER_SETUP.md)。

## 前置要求

1. **确保 Docker Desktop 已启动**
2. **检查 Docker 服务状态**：`docker ps`
3. **确保端口未被占用**：3306、6379、9700、9800、9900

## 启动步骤

### 方式一：仅 MySQL + Redis（开发环境直连）

在 **scripts/docker** 下执行：

```powershell
cd scripts\docker
copy .env.example .env
docker compose -f compose-mysql-redis.yml up -d
```

### 方式二：完整启动（MySQL + Redis + Java API + 前端全部容器化）

```powershell
cd scripts/docker
# 需先构建 jar：cd lyedu-api 后运行 .\build-api.ps1
docker compose build api
docker compose up -d
```

### 方式三：分步启动（用于调试）

```powershell
docker-compose up -d mysql redis
Start-Sleep -Seconds 30
docker-compose up -d api
Start-Sleep -Seconds 60
docker-compose up -d admin pc
```

## 常见问题

### 1. Docker Desktop 未运行
打开 Docker Desktop 应用，等待状态显示为 "Running"。

### 2. 端口被占用
```powershell
netstat -ano | findstr :3306
```

### 3. 构建失败
```powershell
docker-compose build --no-cache api
```

### 4. 数据库连接失败
确保 MySQL 容器已完全启动，首次启动需要 30-60 秒。

## 验证部署

- 管理后台: http://localhost:9900
- PC端: http://localhost:9800
- API: http://localhost:9700/api/hello

## 停止服务

```powershell
docker-compose down
```
