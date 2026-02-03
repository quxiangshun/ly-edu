# LyEdu - 企业培训系统

LyEdu 是一个 100% 开源的企业培训系统，界面美观，操作简单，一键部署您的私有化培训平台！

LyEdu 采用**前后端分离**架构：前端为 Vue3，后端提供 **Java（SpringBoot 4）** 与 **Python（FastAPI）** 两套实现，可任选其一或对照使用；数据库为 MySQL，迁移脚本同时支持 Flyway（Java）与 Alembic（Python）。

## 项目特色

- 🎯 **功能完善**：部门/学员管理、在线视频学习、进度追踪、课程评论、知识中心、周期任务、新员工任务、考试中心、证书、积分与排行、图片库、系统配置、防拖拽/快进等
- 🚀 **双后端**：SpringBoot 4 + JDK 25 与 FastAPI + Python 3，接口对齐，可按团队技术栈选择
- 🎨 **界面美观**：Vue3 + TypeScript + Vite，现代化 UI，管理后台 / PC / H5 多端一致体验
- 🔒 **安全可靠**：视频私有化存储、JWT 认证、飞书集成登录，可配置播放器防拖拽与禁倍速
- 📱 **多端支持**：PC 端、H5 端、管理后台、统一入口

## 技术栈

### 后端（二选一或并行）
- **Java**：SpringBoot 4、JDK 25、MyBatis Plus、MySQL、Flyway 迁移
- **Python**：FastAPI、SQLAlchemy、MySQL、Alembic 迁移

### 前端
- Vue 3、TypeScript、Vite
- Element Plus（管理后台 / PC）、Vant（H5）

### 数据库与迁移
- MySQL 8.0+
- 统一迁移目录 `db/`：`db/flyway/`（Java）、`db/alembic/`（Python），详见 [db/README.md](db/README.md)

## 快速开始

### 环境要求
- **Java 后端**：JDK 25
- **Python 后端**：Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Docker & Docker Compose（可选）

### 本地开发

#### 1. 克隆项目
```bash
git clone <your-repo-url> lyedu
cd lyedu
```

#### 2. 启动后端（任选其一）

**方式 A：Java（Gradle）**
```bash
# 使用构建脚本（推荐）
.\build-api.ps1   # Windows
# 或
./build-api.sh    # Linux/Mac

# 或手动构建
cd lyedu-api
./gradlew bootJar   # Windows: gradlew.bat bootJar
# jar 会复制到根目录 pkg/lyedu-api.jar，然后运行该 jar 启动服务
```

**方式 B：Python**
```bash
cd lyedu-api-python
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
# 配置数据库等环境后启动即可（启动时会自动执行 Alembic 迁移）
uvicorn main:app --reload --host 0.0.0.0 --port 9700
```
也可使用脚本（先迁移再启动）：`.\start.ps1`（Windows）或 `./start.sh`（Linux/Mac）。

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

当前 Docker 默认使用 **Java** 后端。需先本地构建 jar：

```bash
# 1. 构建 jar
.\build-api.ps1   # Windows
# 或
./build-api.sh    # Linux/Mac

# 2. 启动服务
docker-compose build api
docker-compose up -d
```

**国内镜像源**：若访问 Docker Hub 不稳定，可配置 `.env` 中的 `DOCKER_REGISTRY` / `NPM_REGISTRY`。若遇 JDK 25 镜像问题，可参考 [JDK25_DOCKER_FIX.md](docs/JDK25_DOCKER_FIX.md) 或 [QUICK_FIX_JDK25.md](docs/QUICK_FIX_JDK25.md)。

访问地址：
- 管理后台：http://localhost:9900
- PC 端：http://localhost:9800
- H5 端：http://localhost:9801
- API：http://localhost:9700

## 项目结构

```
lyedu/
├── lyedu-api/              # 后端 API（Java，SpringBoot 4）
├── lyedu-api-python/       # 后端 API（Python，FastAPI）
├── lyedu-admin/            # 管理后台前端
├── lyedu-pc/               # PC 端前端
├── lyedu-h5/               # H5 端前端
├── lyedu-entry/            # 统一入口（可选）
├── db/                     # 数据库迁移（Flyway + Alembic）
│   ├── flyway/             # Java 用
│   └── alembic/            # Python 用
├── docker/                 # Docker 相关
├── pkg/                    # 构建产物（如 lyedu-api.jar）
├── docs/                   # 项目文档
└── README.md
```

更多结构说明见 [项目结构说明](docs/PROJECT_STRUCTURE.md)。

## 功能模块

功能设计对照 [PlayEdu 功能明细](https://www.playeduos.com/function.html)，详见 [功能设计文档](docs/FEATURES_DESIGN.md)。

**已实现**
- [x] 用户/部门管理（含入职日期）
- [x] 课程管理（章节、视频、附件、封面从图片库选择）
- [x] 视频学习与进度追踪、课程可见性（部门）
- [x] 课程评论（多级、管理员回复）
- [x] 知识库 / 知识中心、文档在线预览（PDF）
- [x] 数据统计与导出（概览、排行、资源统计、CSV 导出）
- [x] 考试中心（试题库、试卷、考试任务、成绩）
- [x] 证书与证书模板、学习/考试合格关联
- [x] 周期任务、新员工任务（按入职时间）、闯关与颁证
- [x] 系统配置（网站/播放器/学员端设置）
- [x] 积分规则、积分流水、积分排行（学员端「我的积分」）
- [x] 图片库（上传/管理、课程封面选择）
- [x] 防拖拽/快进（配置项，PC/H5 播放器生效）
- [x] 飞书登录、统一入口、PC / H5 / 管理后台

**计划中（P2 等）**
- [ ] 线下课（场次、签到）
- [ ] 积分商城（可选）
- [ ] 防挂机、防录屏/水印
- [ ] 存储扩展（OSS/MinIO）、视频 HLS 加密
- [ ] 扩展集成登录（钉钉、企微、CAS、通讯录同步）

## 许可证

本项目采用 MIT 许可证。

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
