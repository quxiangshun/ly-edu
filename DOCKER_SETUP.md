# Docker 部署指南

## 前置要求

1. **确保 Docker Desktop 已启动**
   - Windows: 打开 Docker Desktop 应用，确保状态为 "Running"
   - 如果 Docker Desktop 未运行，请先启动它

2. **检查 Docker 服务状态**
   ```powershell
   docker ps
   ```
   如果出现 "Access is denied" 错误，请：
   - 以管理员身份运行 PowerShell
   - 或者重启 Docker Desktop

3. **确保端口未被占用**
   - 3306 (MySQL)
   - 6379 (Redis)
   - 9700 (API)
   - 9800 (PC端)
   - 9801 (H5端)
   - 9900 (管理后台)

## 启动步骤

### 方式一：完整启动（推荐）

```powershell
# 1. 确保在项目根目录
cd d:\Users\73559\IdeaProjects\LyEdu

# 2. 启动所有服务（后台运行）
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 查看服务状态
docker-compose ps
```

### 方式二：分步启动（用于调试）

```powershell
# 1. 先启动数据库服务
docker-compose up -d mysql redis

# 2. 等待数据库就绪（约30秒）
Start-Sleep -Seconds 30

# 3. 启动后端 API
docker-compose up -d api

# 4. 等待 API 就绪（约60秒）
Start-Sleep -Seconds 60

# 5. 启动前端服务
docker-compose up -d admin pc h5
```

## 常见问题

### 1. Docker Desktop 未运行

**错误信息：**
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: Access is denied
```

**解决方法：**
1. 打开 Docker Desktop 应用
2. 等待 Docker Desktop 完全启动（状态显示为 "Running"）
3. 如果仍然失败，尝试重启 Docker Desktop

### 2. 端口被占用

**错误信息：**
```
Bind for 0.0.0.0:3306 failed: port is already allocated
```

**解决方法：**
1. 检查端口占用：
   ```powershell
   netstat -ano | findstr :3306
   ```
2. 停止占用端口的服务，或修改 `compose.yml` 中的端口映射

### 3. 构建失败

**后端 API 构建失败：**
- 确保网络连接正常（需要下载 Maven 依赖）
- 首次构建可能需要较长时间（5-10分钟）
- 如果失败，可以尝试：
  ```powershell
  docker-compose build --no-cache api
  ```

**前端构建失败：**
- 确保 package.json 中的依赖版本正确
- 可以尝试单独构建：
  ```powershell
  cd lyedu-admin
  docker build -t lyedu-admin .
  ```

### 4. 数据库连接失败

**错误信息：**
```
Communications link failure
```

**解决方法：**
1. 确保 MySQL 容器已完全启动：
   ```powershell
   docker-compose logs mysql
   ```
2. 等待 MySQL 初始化完成（首次启动需要30-60秒）
3. 检查数据库初始化脚本是否存在：
   ```powershell
   Test-Path docker\mysql\init.sql
   ```

## 验证部署

### 1. 检查所有容器状态

```powershell
docker-compose ps
```

所有服务应该显示为 "Up" 状态。

### 2. 访问服务

- 管理后台: http://localhost:9900
- PC端: http://localhost:9800
- H5端: http://localhost:9801
- API: http://localhost:9700/api/hello

### 3. 查看日志

```powershell
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs api
docker-compose logs mysql
```

## 停止服务

```powershell
# 停止所有服务
docker-compose down

# 停止并删除数据卷（注意：会删除数据库数据）
docker-compose down -v
```

## 清理

```powershell
# 停止并删除容器、网络
docker-compose down

# 删除未使用的镜像
docker image prune

# 删除所有未使用的资源（谨慎使用）
docker system prune -a
```
