# LyEdu 目录与文件说明

本文档说明仓库中主要目录和文件的作用，便于新人快速了解项目结构。

---

## 仓库根目录

| 文件/目录 | 作用 |
|-----------|------|
| **README.md** | 项目介绍、快速开始、技术栈、功能列表、许可证与支持说明 |
| **LICENSE** | Apache 2.0 开源协议全文 |
| **.gitignore** | Git 忽略规则（如 node_modules、.env 等） |
| **scripts/docker/** | Docker 用 `.env.example`、`compose-mysql-redis.yml` 等，见 [scripts/README.md](../scripts/README.md) |
| **scripts/** | 脚本与配置目录：**dev/** 一键启动/停止，**docker/** 下 .env 与 compose 组合使用。详见 [scripts/README.md](../scripts/README.md) |

---

## docker/ — Docker 相关

| 文件/目录 | 作用 |
|-----------|------|
| **docker/mysql/init.sql** | MySQL 容器首次启动时执行：root@'%'、创建 lyedu 库；表结构由 Alembic 创建 |

---

## docs/ — 项目文档

| 文件 | 作用 |
|------|------|
| **PROJECT_STRUCTURE.md** | 项目结构、技术选型、开发规范、部署说明 |
| **FILE_STRUCTURE.md** | 本文件：目录与每个文件的作用说明 |
| **DOCKER_SETUP.md** | Docker 部署步骤、常见问题 |
| **FEISHU_APP.md** | 飞书应用配置与登录对接说明 |
| **LOGIN.md** | 多平台登录说明 |
| **LYEDU_API_PYTHON.md** | Python API 详细说明 |
| **配置模板生成及使用指南.md** | LyEdu 配置模板（~/.lyedu/conf）使用指南 |
| **SUPPORT.md** | 用户支持与打赏说明 |

---

## lyedu-api-python/ — 后端 API（Python，FastAPI）

| 文件/目录 | 作用 |
|-----------|------|
| **main.py** | FastAPI 应用入口；启动时执行 Alembic 迁移，再挂载路由 |
| **config.py** | 配置（MySQL、Redis、飞书、JWT 等；优先 ~/.lyedu/conf/config.ini，否则 .env） |
| **lyedu_config.py** | LyEdu 配置模板生成与加载 |
| **db.py** | MySQL 连接（pymysql） |
| **requirements.txt** | Python 依赖 |
| **alembic.ini** | Alembic 配置（script_location = alembic） |
| **.env.example** | 环境变量模板 |
| **.env.dev** / **.env.prod** | 开发/生产环境预设 |
| **Dockerfile** | 构建 Python API 镜像 |
| **docker-entrypoint.sh** | 容器入口：等 MySQL 就绪 → alembic upgrade head → uvicorn |
| **install.ps1** / **install.bat** | Windows 下安装依赖与虚拟环境 |
| **start.ps1** / **start.sh** | 先执行 Alembic 迁移再启动 uvicorn |
| **routers/** | 路由模块（auth、course、chapter、video、user、department、feishu 等） |
| **services/** | 业务逻辑层，按域分子目录 |
| **models/schemas.py** | Pydantic 请求/响应模型 |
| **common/result.py** | 统一响应结构 |
| **alembic/** | 数据库迁移脚本（env.py、versions/）；启动时自动执行 |
| **util/** | JWT、飞书 API 等 |

---

## lyedu-admin/ — 管理后台前端（Vue3 + Element Plus）

| 文件/目录 | 作用 |
|-----------|------|
| **package.json** / **vite.config.ts** / **tsconfig.json** | 依赖与构建配置 |
| **src/main.ts** | 应用入口 |
| **src/router/index.ts** | 路由与菜单对应 |
| **src/utils/request.ts** | Axios 封装、baseURL、鉴权 |
| **src/api/*.ts** | 各模块 API 封装 |
| **src/views/** | 页面组件（Dashboard、User、Course、Exam、Settings 等） |

---

## lyedu-pc/ — PC 端学员前端（Vue3 + Element Plus）

| 文件/目录 | 作用 |
|-----------|------|
| **package.json** / **vite.config.ts** / **tsconfig.json** | 同管理后台，为 PC 端独立工程 |
| **.env.example** | 环境变量示例（API 地址等） |
| **src/router/index.ts** | PC 端路由（登录、首页、课程、学习、考试、任务、证书等） |
| **src/utils/auth.ts** | 登录态、token 存储与校验 |
| **src/views/** | 课程、学习、考试、任务、证书、积分等页面 |

---

## lyedu-unix/ — 学员端 H5/微信小程序（uni-app x）

| 文件/目录 | 作用 |
|-----------|------|
| **pages.json** | 页面与路由配置 |
| **manifest.json** | 应用与平台配置 |
| **api/** | 接口封装 |
| **config/api.uts** / **config/auth.uts** | API 地址、登录方式 |
| **pages/** | 页面（首页、课程、我的、登录、学习、考试等） |
| **utils/** | 请求、鉴权等工具 |

---

## lyedu-entry/ — 统一入口（可选）

| 文件/目录 | 作用 |
|-----------|------|
| **ENTRY_CONFIG.md** | 统一入口配置说明 |
| **.env.example** | 环境变量示例 |
| **index.html** / **src/App.vue** 等 | 简单入口页，可跳转到 admin/pc/h5 或登录选择端 |

---

## 小结

- **根目录**：README、许可证、 scripts。
- **scripts/**：开发环境一键脚本（dev）、Docker 用 .env+compose 组合（docker）。
- **docker/**：MySQL 容器初始化 SQL。
- **docs/**：结构、部署、功能、飞书、支持等文档。
- **lyedu-api-python/**：Python 后端（FastAPI、Alembic 自动迁移）。
- **lyedu-admin/**：管理后台。
- **lyedu-pc/**：PC 学员端。
- **lyedu-unix/**：学员端 H5/微信小程序（uni-app x）。
- **lyedu-entry/**：可选统一入口。

更多细节可参考 **README.md** 与 **docs/PROJECT_STRUCTURE.md**。
