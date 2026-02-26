# LyEdu - 企业培训系统

LyEdu 是一个 100% 开源的企业培训系统，界面美观，操作简单，一键部署您的私有化培训平台！

LyEdu 采用**前后端分离**架构：前端为 Vue3，后端为 **Python（FastAPI）**；数据库为 MySQL，使用 Alembic 进行迁移。

## 项目特色

- 🎯 **功能完善**：部门/学员管理、在线视频学习、进度追踪、课程评论、知识中心、周期任务、新员工任务、考试中心、证书、积分与排行、图片库、系统配置、防拖拽/快进等
- 🚀 **Python 后端**：FastAPI + Python 3.10+，轻量高效
- 🎨 **界面美观**：Vue3 + TypeScript + Vite，现代化 UI，管理后台 / PC / 学员端多端一致体验
- 🔒 **安全可靠**：视频私有化存储、JWT 认证、飞书集成登录，可配置播放器防拖拽与禁倍速
- 📱 **多端支持**：PC 端、学员端（H5/微信小程序，uni-app x）、管理后台、统一入口

## 技术栈

### 后端
- **Python**：FastAPI、PyMySQL、MySQL、Alembic 迁移

### 前端
- Vue 3、TypeScript、Vite
- Element Plus（管理后台 / PC）、uni-app x（学员端 H5/小程序）

### 数据库与迁移
- MySQL 8.0+
- 统一迁移目录 `db/alembic/`，详见 [db/README.md](db/README.md)

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Docker & Docker Compose（可选）

### 本地开发

#### 一键启动开发环境（Windows，项目根目录）

开发环境脚本与配置在 **scripts/** 下，详见 [scripts/README.md](scripts/README.md)。

**1. 配置**（首次或需改连接时）

- 复制 `scripts/dev/dev-config.example.yml` 为 `scripts/dev/dev-config.yml`，按需修改：
  - **database** / **redis**：MySQL、Redis 连接信息（供 lyedu-api-python 使用；`database.port` 也用于判断是否自动启动 Docker MySQL+Redis）
  - **start_docker_mysql_redis**：为 `true` 时，若本机未监听 MySQL 端口则自动执行 `docker compose` 启动 MySQL+Redis
  - **start_lyedu_api_python** / **start_lyedu_admin** / **start_lyedu_pc**：是否启动对应服务（true/false）

**2. 启动与停止**

在项目根目录执行：

```powershell
.\scripts\dev\start.ps1   # 按 dev-config.yml 初始化环境（.venv、npm install、可选 Docker），在新终端中启动各服务
.\scripts\dev\stop.ps1    # 关闭上述终端，并结束占用 9700/9800/9900 端口的进程
```

#### 手动启动

**1. 克隆项目**
```bash
git clone https://github.com/quxiangshun/ly-edu.git
cd ly-edu
```

**2. 启动数据库**（可选，若使用自有数据库则跳过）

```bash
cd scripts/docker
docker compose -f compose-mysql-redis.yml up -d
```

**3. 启动后端（Python）**
```bash
cd lyedu-api-python
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
ENV=dev uvicorn main:app --reload --host 0.0.0.0 --port 9700
```

也可使用一键脚本：`.\scripts\dev\start.ps1`。启动时会自动执行 Alembic 迁移。

**4. 启动前端**
```bash
# 管理后台
cd lyedu-admin
npm install
npm run dev

# PC 端
cd lyedu-pc
npm install
npm run dev

# 学员端 H5/小程序（uni-app x）
使用 HBuilderX 打开 lyedu-unix 项目，运行到浏览器或微信开发者工具。
```

### Docker 部署

**方式一：仅 MySQL + Redis**

```bash
cd scripts/docker
copy .env.example .env
docker compose -f compose-mysql-redis.yml up -d
```

数据库就绪后，本地启动 lyedu-api-python、lyedu-admin、lyedu-pc。详见 [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)。

**国内镜像源**：在 **scripts/docker/** 下复制 `.env.example` 为 `.env`，配置 `DOCKER_REGISTRY` / `NPM_REGISTRY`。

访问地址：
- 管理后台：http://localhost:9900
- PC 端：http://localhost:9800
- API：http://localhost:9700
- 学员端 H5/小程序：使用 lyedu-unix 运行到浏览器或微信开发者工具

## 项目结构

```
lyedu/
├── lyedu-api-python/       # 后端 API（Python，FastAPI）
├── lyedu-admin/            # 管理后台前端
├── lyedu-pc/               # PC 端前端
├── lyedu-unix/             # 学员端 H5/小程序（uni-app x）
├── lyedu-entry/            # 统一入口（可选）
├── db/                     # 数据库迁移（Alembic）
│   └── alembic/            # Python 用
├── scripts/                # 脚本与配置（dev 一键启动、docker），见 scripts/README.md
├── docs/                   # 项目文档
└── README.md
```

更多结构说明见 [项目结构说明](docs/PROJECT_STRUCTURE.md)。

## 功能模块

功能设计对照 [PlayEdu 功能明细](https://www.playeduos.com/function.html)。

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
- [x] 第三方配置（飞书/钉钉/企微，管理后台可选择），飞书通讯录同步已实现，钉钉/企微预留

**计划中（P2 等）**
- [ ] 线下课（场次、签到）
- [ ] 积分商城（可选）
- [ ] 防挂机、防录屏/水印
- [ ] 存储扩展（OSS/MinIO）、视频 HLS 加密
- [ ] 扩展集成登录（钉钉、企微、CAS、通讯录同步）

## 许可证

本项目采用 Apache 2.0 许可证，详见 [LICENSE](LICENSE)。

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
