# LyEdu 目录与文件说明（Java 版，含 lyedu-api）

> **说明**：lyedu-api（Java 后端）已暂停维护，本文档仅供历史参考。当前目录说明见 [FILE_STRUCTURE.md](FILE_STRUCTURE.md)。

本文档说明仓库中主要目录和文件的作用，便于新人快速了解项目结构。

---

## 仓库根目录

| 文件/目录 | 作用 |
|-----------|------|
| **README.md** | 项目介绍、快速开始、技术栈、功能列表、许可证与支持说明 |
| **LICENSE** | Apache 2.0 开源协议全文 |
| **.gitignore** | Git 忽略规则（如 node_modules、target、.env 等） |
| **scripts/docker/** | Docker 用 `.env.example`、`compose.yml`、`compose-mysql-redis.yml` 组合使用 |
| **pkg/** | 构建产物目录，存放 lyedu-api.jar 等（由 lyedu-api/build-api.ps1 生成） |
| **scripts/** | 脚本与配置目录：**dev/** 一键启动/停止，**docker/** 下 .env 与 compose 组合使用 |

---

## lyedu-api/ — 后端 API（Java，SpringBoot 4，已暂停维护）

| 文件/目录 | 作用 |
|-----------|------|
| **init-gradle.ps1** | Windows 下初始化 Gradle 包装器 |
| **build-api.ps1** / **build-api.sh** | 构建 jar 并复制到 pkg/lyedu-api.jar |
| **build.gradle** / **settings.gradle** | Gradle 构建配置 |
| **Dockerfile** | 构建 Java API 镜像 |
| **src/main/java/com/lyedu/** | Java 源码包 |
| **src/main/resources/application*.yml** | 应用配置 |

---

## lyedu-api-python/ — 后端 API（Python，FastAPI）

（同 FILE_STRUCTURE.md 中的 lyedu-api-python 节）

---

## lyedu-admin/、lyedu-pc/、lyedu-unix/、lyedu-entry/

（同 FILE_STRUCTURE.md）

---

更多细节可参考 **README.md** 与 **docs/PROJECT_STRUCTURE.md**。
