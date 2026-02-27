# Docker 部署指南

## 前置要求

1. **确保 Docker Desktop 已启动**
   - Windows: 打开 Docker Desktop 应用，确保状态为 "Running"
   - 若出现 "Access is denied" 错误，以管理员身份运行 PowerShell 或重启 Docker Desktop

2. **检查 Docker 服务状态**
   ```powershell
   docker ps
   ```

3. **确保端口未被占用**
   - 3306 (MySQL)
   - 6379 (Redis)
   - 9700 (API)
   - 9800 (PC 端)
   - 9900 (管理后台)

## 启动步骤

### 方式一：仅 MySQL + Redis（推荐开发环境）

仅启动数据库，本地跑 Python API 和前端。进入 **scripts/docker** 后执行：

```powershell
cd scripts\docker
copy .env.example .env
docker compose -f compose-mysql-redis.yml up -d
```

- **MySQL**：localhost:3306（root / Lyedu@123，库 lyedu）
- **Redis**：localhost:6379
- 本地启动 lyedu-api-python、lyedu-admin、lyedu-pc 等直连上述地址；Python 启动时会自动执行 Alembic 迁移。

### 方式二：完整编排（MySQL + Redis + Python API + 前端）

在 **scripts/docker** 下执行（会构建并启动所有服务）：

```powershell
cd scripts\docker
copy .env.example .env
docker compose up -d
```

- **API**：http://localhost:9700
- **管理后台**：http://localhost:9900
- **PC 端**：http://localhost:9800

### 方式三：仅数据库 + 本地运行前端

1. 按方式一启动 MySQL + Redis
2. 按 [README.md](../README.md) 启动 lyedu-api-python、lyedu-admin、lyedu-pc
3. 或使用一键脚本：`.\scripts\dev\start.ps1`

## 常见问题

### 1. Docker Desktop 未运行

**错误信息：**
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: Access is denied
```

**解决方法**：打开 Docker Desktop，等待完全启动（状态为 "Running"）；若仍失败，重启 Docker Desktop。

### 2. 端口被占用

**错误信息：**
```
Bind for 0.0.0.0:3306 failed: port is already allocated
```

**解决方法**：
```powershell
netstat -ano | findstr :3306
```
停止占用端口的服务，或修改 `scripts/docker/compose-mysql-redis.yml` 中的端口映射。

### 3. 数据库连接失败

**错误信息：**
```
Communications link failure
```

**解决方法**：
1. 确保 MySQL 容器已完全启动：`docker compose -f compose-mysql-redis.yml logs mysql`
2. 首次启动需要 30-60 秒初始化
3. 检查 `docker/mysql/init.sql` 是否存在

## 验证部署

### 1. 检查容器状态

```powershell
cd scripts\docker
docker compose -f compose-mysql-redis.yml ps
```

### 2. 访问服务

本地启动 API 与前端后：
- 管理后台: http://localhost:9900
- PC 端: http://localhost:9800
- API: http://localhost:9700/docs

## 停止服务

```powershell
cd scripts\docker
docker compose -f compose-mysql-redis.yml down
```

如需删除数据卷（会删除数据库数据）：
```powershell
docker compose -f compose-mysql-redis.yml down -v
```
