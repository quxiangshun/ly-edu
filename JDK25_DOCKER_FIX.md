# JDK 25 Docker 镜像问题解决方案

## 问题描述

Docker 构建时无法下载 `eclipse-temurin:25-jre-jammy` 或 `maven:3.9-eclipse-temurin-25` 镜像，可能是：
1. 网络连接问题（Docker Hub 访问受限）
2. 镜像标签不存在或已更改
3. 需要配置 Docker 镜像加速器

## 解决方案

### 方案 1: 配置 Docker 镜像加速器（推荐）

**Windows Docker Desktop 配置：**

1. 打开 Docker Desktop
2. 点击设置 (Settings) → Docker Engine
3. 添加以下配置：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```
4. 点击 "Apply & Restart"

**或者手动编辑配置文件：**
- 文件位置：`%USERPROFILE%\.docker\daemon.json`
- 添加上述配置后重启 Docker Desktop

### 方案 2: 使用备选镜像源

如果 `eclipse-temurin` 镜像无法下载，可以使用 Microsoft OpenJDK 25：

**修改 compose.yml：**
```yaml
api:
  build:
    context: ./lyedu-api
    dockerfile: Dockerfile.alternative  # 使用备选 Dockerfile
```

**或者直接修改 Dockerfile：**
将 `lyedu-api/Dockerfile` 中的镜像改为：
```dockerfile
FROM mcr.microsoft.com/openjdk/jdk:25-ubuntu AS builder
# 需要手动安装 Maven
```

### 方案 3: 手动构建（如果镜像都不可用）

使用 `Dockerfile.build-jdk25`，它会自动下载 JDK 25：

```powershell
# 修改 compose.yml 中的 dockerfile
dockerfile: Dockerfile.build-jdk25

# 或者直接构建
cd lyedu-api
docker build -f Dockerfile.build-jdk25 -t lyedu-api .
```

### 方案 4: 使用代理（如果有）

如果您的网络需要代理：

1. 配置 Docker Desktop 代理：
   - Settings → Resources → Proxies
   - 配置 HTTP/HTTPS 代理

2. 或者在命令行设置：
```powershell
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"
docker-compose up --build
```

## 验证镜像是否存在

```powershell
# 检查 eclipse-temurin JDK 25
docker pull eclipse-temurin:25-jdk-jammy

# 检查 Microsoft OpenJDK 25
docker pull mcr.microsoft.com/openjdk/jdk:25-ubuntu

# 检查 Maven with JDK 25
docker pull maven:3.9-eclipse-temurin-25
```

## 快速修复脚本

运行 `fix-jdk25-docker.ps1` 脚本，它会：
1. 尝试配置镜像加速器
2. 测试镜像下载
3. 如果失败，自动切换到备选方案

```powershell
.\fix-jdk25-docker.ps1
```

## 推荐的镜像标签

根据 Eclipse Temurin 官方文档，JDK 25 的正确标签格式：

- `eclipse-temurin:25-jdk-jammy` - JDK 25 (Ubuntu Jammy)
- `eclipse-temurin:25-jre-jammy` - JRE 25 (Ubuntu Jammy)
- `eclipse-temurin:25.0.1-jdk-jammy` - 指定版本号

Maven 镜像：
- `maven:3.9-eclipse-temurin-25` - Maven 3.9 with JDK 25
- 如果不存在，可以手动构建或使用基础镜像安装 Maven

## 如果所有方案都失败

最后的选择是使用 JDK 21 (LTS)，但需要修改代码：

1. 修改 `pom.xml`：
```xml
<java.version>21</java.version>
```

2. 修改 `Dockerfile`：
```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS builder
FROM eclipse-temurin:21-jre-jammy
```

**注意：** 用户要求必须使用 JDK 25，所以此方案仅作为最后备选。
