# JDK 25 Docker 问题快速修复

## 问题
```
failed to solve: eclipse-temurin:25-jre-jammy: failed to resolve source metadata
```

## 快速解决方案（按顺序尝试）

### 方案 1: 配置 Docker 镜像加速器（最快）

1. **打开 Docker Desktop**
2. **Settings → Docker Engine**
3. **添加以下配置：**
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```
4. **Apply & Restart**
5. **重新运行：**
```powershell
docker-compose up --build
```

### 方案 2: 测试镜像可用性

运行测试脚本：
```powershell
.\test-jdk25-images.ps1
```

根据结果选择对应的 Dockerfile。

### 方案 3: 使用备选 Dockerfile

如果标准镜像无法下载，修改 `compose.yml`：

```yaml
api:
  build:
    context: ./lyedu-api
    dockerfile: Dockerfile.manual-maven  # 或 Dockerfile.alternative
```

**可用的备选 Dockerfile：**
- `Dockerfile.manual-maven` - 使用基础 JDK 25 镜像，手动安装 Maven
- `Dockerfile.alternative` - 使用 Microsoft OpenJDK 25
- `Dockerfile.build-jdk25` - 完全手动下载安装 JDK 25

### 方案 4: 手动拉取镜像

```powershell
# 尝试不同的标签
docker pull eclipse-temurin:25-jdk-jammy
docker pull eclipse-temurin:25.0.1-jdk-jammy
docker pull maven:3.9-eclipse-temurin-25
docker pull mcr.microsoft.com/openjdk/jdk:25-ubuntu
```

找到可用的镜像后，修改 Dockerfile 使用对应的标签。

### 方案 5: 使用代理（如果有）

如果您的网络需要代理：

1. **Docker Desktop → Settings → Resources → Proxies**
2. 配置 HTTP/HTTPS 代理
3. 重启 Docker Desktop

## 推荐操作流程

1. ✅ 先配置镜像加速器（方案 1）
2. ✅ 运行测试脚本（方案 2）
3. ✅ 根据结果选择对应的 Dockerfile（方案 3）
4. ✅ 重新构建

## 验证

构建成功后，验证 JDK 版本：
```powershell
docker-compose exec api java -version
```

应该显示：
```
openjdk version "25" ...
```

## 如果所有方案都失败

最后的选择是使用网络代理或 VPN，或者联系网络管理员配置 Docker Hub 访问。
