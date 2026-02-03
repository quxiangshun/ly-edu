# LyEdu - 企业培训系统

LyEdu 是一个 100% 开源的企业培训系统，界面美观，操作简单，一键部署您的私有化培训平台！

LyEdu 基于 Java + MySQL 开发，采用前后端分离模式，前端核心框架为 Vue3，后端核心框架为 SpringBoot 4。

## 项目特色

- 🎯 **功能完善**：提供部门管理、学员管理、在线视频学习、学员进度追踪、视频私有化存储等基础培训功能
- 🚀 **技术先进**：SpringBoot 4 + JDK 25 + Vue3，采用前后端分离架构
- 🎨 **界面美观**：现代化 UI 设计，用户体验优秀
- 🔒 **安全可靠**：支持视频私有化存储，数据安全有保障
- 📱 **多端支持**：支持 PC 端、H5 端和管理后台

## 技术栈

### 后端
- SpringBoot 4
- JDK 25
- MySQL
- MyBatis Plus

### 前端
- Vue 3
- TypeScript
- Vite
- Element Plus / Ant Design Vue

## 快速开始

### 环境要求
- JDK 25
- Node.js 18+
- MySQL 8.0+
- Docker & Docker Compose（可选）

### 本地开发

#### 1. 克隆项目
```bash
git clone <your-repo-url> lyedu
cd lyedu
```

#### 2. 构建后端（使用 Gradle）
```bash
# 方式一：使用构建脚本（推荐）
.\build-api.ps1  # Windows
# 或
./build-api.sh   # Linux/Mac

# 方式二：手动构建
cd lyedu-api
./gradlew bootJar  # Windows: gradlew.bat bootJar
# jar 会自动复制到根目录 pkg/lyedu-api.jar
```

#### 3. 启动前端
```bash
# 管理后台
cd lyedu-admin
npm install
npm run dev

# PC 端
cd lyedu-pc
npm install
npm run dev

# H5 端
cd lyedu-h5
npm install
npm run dev
```

### Docker 部署

**重要：** Docker 构建已简化，不再在容器内构建。需要先本地构建 jar：

```bash
# 1. 先构建 jar（使用 Gradle）
.\build-api.ps1  # Windows
# 或
./build-api.sh   # Linux/Mac

# 2. 然后启动 Docker 服务
docker-compose build api
docker-compose up -d
```

**国内镜像源（推荐）**：如果你在国内访问 Docker Hub 不稳定，请先配置 `.env` 里的 `DOCKER_REGISTRY` / `NPM_REGISTRY`，项目已支持在构建阶段走国内源。

**重要：** 如果仍遇到 JDK 25 镜像下载问题，请先查看 [JDK25_DOCKER_FIX.md](docs/JDK25_DOCKER_FIX.md) 或 [QUICK_FIX_JDK25.md](docs/QUICK_FIX_JDK25.md)

#### 国内镜像源示例

编辑根目录 `.env`：

```bash
# 阿里云（示例：按你实际可用的前缀填写）
DOCKER_REGISTRY=registry.cn-hangzhou.aliyuncs.com/library/
MAVEN_MIRROR=https://maven.aliyun.com/repository/public
NPM_REGISTRY=https://registry.npmmirror.com
```

然后重新构建：

```bash
docker-compose build --no-cache api
docker-compose up -d
```

#### 自动换一个可用镜像（推荐）

如果你不想一直试某一个镜像源，直接运行：

```bash
.\switch-docker-registry.ps1
docker-compose build --no-cache api
docker-compose up -d
```

访问地址：
- 管理后台：http://localhost:9900
- PC 端：http://localhost:9800
- H5 端：http://localhost:9801
- API 端口：http://localhost:9700

## 项目结构

```
lyedu/
├── lyedu-api/          # 后端 API 服务
├── lyedu-admin/        # 管理后台前端
├── lyedu-pc/           # PC 端前端
├── lyedu-h5/           # H5 端前端
├── docker/             # Docker 配置文件
├── compose.yml         # Docker Compose 配置
├── docs/               # 项目文档（Docker、Gradle、结构说明等）
└── README.md           # 项目说明
```

## 功能模块

- [x] 用户管理
- [x] 部门管理
- [x] 课程管理
- [x] 视频学习
- [x] 学习进度追踪
- [x] 数据统计

## 开发计划

- [ ] 在线考试
- [ ] 学习任务
- [ ] 文档在线预览
- [ ] 学习证书
- [ ] 数据报表

## 许可证

本项目采用 Apache-2.0 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持我们

LyEdu 开源免费使用。若对您有帮助，欢迎 [Star](https://github.com/quxiangshun/ly-edu) 或通过下方打赏支持我们，感谢您的鼓励与认可。

感谢每一位使用、反馈和推荐 LyEdu 的朋友；以爱之名，为教育赋能。

| 支付宝 | 微信 |
|--------|------|
| ![支付宝收款码](docs/支付宝收款码.jpg) | ![微信收款码](docs/微信收款码.jpg) |

更多感谢与说明见 [用户支持说明](docs/SUPPORT.md)。

## 关于

LyEdu - 以爱之名，为教育赋能 💝

---

**注意**：本项目为完全原创，不包含任何第三方项目的代码。
