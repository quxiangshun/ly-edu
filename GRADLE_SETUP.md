# Gradle 构建配置说明

## 从 Maven 迁移到 Gradle

项目已从 Maven 迁移到 Gradle，构建流程已简化：

1. **本地构建**：使用 Gradle 在本地构建 jar
2. **Docker 运行**：Docker 只负责运行已构建的 jar，不再构建

## 初始化 Gradle Wrapper

首次使用需要初始化 Gradle Wrapper：

### Windows
```powershell
.\init-gradle.ps1
```

### Linux/Mac
```bash
cd lyedu-api
gradle wrapper --gradle-version 8.10.2
# 或如果已安装 Gradle
./gradlew wrapper --gradle-version 8.10.2
```

如果系统没有安装 Gradle，可以手动下载 Wrapper jar：

1. 下载：https://raw.githubusercontent.com/gradle/gradle/v8.10.2/gradle/wrapper/gradle-wrapper.jar
2. 放到：`lyedu-api/gradle/wrapper/gradle-wrapper.jar`

## 构建项目

### 方式一：使用构建脚本（推荐）

**Windows:**
```powershell
.\build-api.ps1
```

**Linux/Mac:**
```bash
./build-api.sh
```

### 方式二：手动构建

```bash
cd lyedu-api
./gradlew bootJar  # Windows: gradlew.bat bootJar
```

构建完成后，jar 会自动复制到根目录 `pkg/lyedu-api.jar`

## Docker 部署

构建好 jar 后，启动 Docker：

```bash
docker-compose build api
docker-compose up -d
```

## 构建配置

- **Gradle 版本**: 8.10.2
- **Java 版本**: 25
- **Spring Boot 版本**: 4.0.0
- **构建工具**: Spring Boot Gradle Plugin

## 国内镜像源

Gradle 构建已配置使用阿里云 Maven 镜像，依赖下载会更快。

## 常见问题

### Q: 找不到 gradlew 命令
A: 先运行 `.\init-gradle.ps1` 初始化 Wrapper

### Q: 构建失败，提示找不到依赖
A: 检查网络连接，确保能访问 Maven 仓库（已配置阿里云镜像）

### Q: jar 文件没有复制到 pkg 目录
A: 检查 `build.gradle` 中的 `bootJar` 任务配置，确保 `doLast` 块正确执行
