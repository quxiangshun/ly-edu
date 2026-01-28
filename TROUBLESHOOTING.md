# 故障排查指南

## Docker 相关问题

### 问题 1: Docker Desktop 未运行

**错误信息：**
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: Access is denied
```

**解决方案：**
1. 打开 Docker Desktop 应用程序
2. 等待 Docker Desktop 完全启动（状态栏显示 "Running"）
3. 如果仍然失败，尝试：
   - 以管理员身份运行 PowerShell
   - 重启 Docker Desktop
   - 检查 Windows 服务中 Docker Desktop Service 是否运行

### 问题 2: 端口被占用

**错误信息：**
```
Bind for 0.0.0.0:3306 failed: port is already allocated
```

**解决方案：**
1. 检查端口占用：
   ```powershell
   netstat -ano | findstr :3306
   ```
2. 停止占用端口的进程，或修改 `compose.yml` 中的端口映射

### 问题 3: 构建失败 - Maven 依赖下载失败

**错误信息：**
```
[ERROR] Failed to execute goal ... Could not resolve dependencies
```

**解决方案：**
1. 检查网络连接
2. 配置 Maven 镜像（如果需要）：
   在 `lyedu-api/pom.xml` 中添加：
   ```xml
   <repositories>
       <repository>
           <id>aliyun</id>
           <url>https://maven.aliyun.com/repository/public</url>
       </repository>
   </repositories>
   ```
3. 清理并重新构建：
   ```powershell
   docker-compose build --no-cache api
   ```

### 问题 4: 构建失败 - JDK 25 镜像不存在

**错误信息：**
```
failed to solve: failed to fetch ... openjdk:25-jdk-slim
```

**解决方案：**
如果 JDK 25 镜像不存在，可以修改 `lyedu-api/Dockerfile`：
```dockerfile
# 使用 JDK 21 (LTS)
FROM eclipse-temurin:21-jdk-jammy AS builder
```

同时修改 `pom.xml` 中的 Java 版本：
```xml
<java.version>21</java.version>
```

### 问题 5: 数据库连接失败

**错误信息：**
```
Communications link failure
```

**解决方案：**
1. 确保 MySQL 容器已完全启动：
   ```powershell
   docker-compose logs mysql
   ```
2. 等待 MySQL 初始化完成（首次启动需要30-60秒）
3. 检查数据库初始化脚本：
   ```powershell
   Test-Path docker\mysql\init.sql
   ```
4. 如果脚本不存在，创建它或移除 volume 映射

### 问题 6: 前端构建失败

**错误信息：**
```
npm ERR! code ELIFECYCLE
```

**解决方案：**
1. 检查 `package.json` 中的依赖版本
2. 清理 node_modules 并重新安装：
   ```powershell
   cd lyedu-admin
   Remove-Item -Recurse -Force node_modules
   npm install
   ```
3. 如果使用 npm 镜像，配置 `.npmrc`：
   ```
   registry=https://registry.npmmirror.com
   ```

## 代码相关问题

### 问题 7: pom.xml 解析错误

**错误信息：**
```
[ERROR] The project cannot be built until build path errors are resolved
```

**解决方案：**
检查 `pom.xml` 中的 XML 标签是否正确：
- `<n>` 应该是 `<name>`
- 所有标签必须正确闭合
- 检查缩进和格式

### 问题 8: Spring Boot 启动失败

**错误信息：**
```
APPLICATION FAILED TO START
```

**解决方案：**
1. 查看详细日志：
   ```powershell
   docker-compose logs api
   ```
2. 检查配置文件 `application.yml`
3. 确保数据库连接信息正确
4. 检查端口是否被占用

## 快速诊断命令

```powershell
# 检查 Docker 状态
docker ps
docker info

# 检查容器日志
docker-compose logs
docker-compose logs api
docker-compose logs mysql

# 检查容器状态
docker-compose ps

# 重启服务
docker-compose restart api

# 完全重建
docker-compose down
docker-compose up --build -d

# 清理所有资源（谨慎使用）
docker-compose down -v
docker system prune -a
```

## 获取帮助

如果以上方法都无法解决问题，请：

1. 收集错误日志：
   ```powershell
   docker-compose logs > error.log
   ```

2. 检查系统信息：
   ```powershell
   docker version
   docker-compose version
   ```

3. 查看容器状态：
   ```powershell
   docker-compose ps
   docker stats
   ```
