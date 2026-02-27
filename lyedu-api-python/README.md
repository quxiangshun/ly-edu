# LyEdu API - Python 版本

与 LyEdu Java (Spring Boot) 后台功能对应的 Python 实现，使用 **FastAPI** + **PyMySQL**，本地 Python 建议 **3.14.2**（兼容 3.10+）。

## 环境

- Python 3.10+（推荐 3.14.2）
- MySQL（与 Java 版共用同一数据库）

## 安装与运行

**请在终端（命令提示符或 PowerShell）里执行以下命令，不要用“打开文件”的方式运行。**

1. 进入项目目录，用 **python -m** 创建虚拟环境（使用 `.venv` 目录名）：

```bash
cd lyedu-api-python
python -m venv .venv
```

若本机只有 `py` 启动器，可用：`py -3 -m venv .venv`。

2. 激活虚拟环境：

- **Windows 命令提示符：** `.venv\Scripts\activate.bat`
- **Windows PowerShell：** `.venv\Scripts\Activate.ps1`
- **Linux/macOS：** `source .venv/bin/activate`

3. 安装依赖（建议使用国内镜像，见下方）：

```bash
pip install -r requirements.txt
```

4. 配置环境（二选一）：

- **方式一（推荐打包/交付）**：使用 `~/.lyedu/conf/config.ini`（见下方「LyEdu 配置模板」）
- **方式二（开发）**：复制 `.env.example` 为 `.env`，或使用 `.env.dev` / `.env.prod`（见下方「环境变量」）

**ENV**：启动前需指定环境。方式一：`ENV=dev uvicorn main:app ...`；方式二：未指定时终端会提示选择 1=dev / 2=prod（5 分钟内无输入将退出）

5. 启动服务（**启动时会自动执行 Alembic 迁移**）：

```bash
# 推荐：明确指定环境
ENV=dev uvicorn main:app --host 0.0.0.0 --port 9700
```

或使用启动脚本（先执行 `alembic upgrade head`，再启动 uvicorn）：

- **PowerShell：** `.\start.ps1`
- **Linux/macOS：** `./start.sh`（需 `chmod +x start.sh`）

**打包可执行文件**：运行 `lyedu_backend`（或 `lyedu_backend.exe`）启动后，控制台会提示「后台服务已启动」，停止方式：在运行窗口按 **Ctrl+C**；也可使用 `.\stop.ps1`（Windows）或 `./stop.sh`（Linux）按端口停止。

### pip 使用国内镜像源

安装依赖时若较慢，可改用国内镜像：

**方式一：单次安装指定镜像**

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**方式二：当前项目默认使用清华源（推荐）**

在项目目录下执行一次：

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

之后该环境下的 `pip install` 都会走清华源。其他常用国内源：

| 镜像     | index-url |
|----------|-----------|
| 清华     | https://pypi.tuna.tsinghua.edu.cn/simple |
| 阿里云   | https://mirrors.aliyun.com/pypi/simple/  |
| 腾讯云   | https://mirrors.cloud.tencent.com/pypi/simple |
| 豆瓣     | https://pypi.douban.com/simple/          |

**方式三：一键脚本（创建 .venv + 用清华源安装）**

- PowerShell：`.\install.ps1`
- 命令提示符：`install.bat`

### 环境变量

- `ENV`：环境标识，`dev` 或 `prod`，用于加载 `.env.dev` / `.env.prod`
- `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USERNAME`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`
- `REDIS_HOST`、`REDIS_PORT`、`REDIS_PASSWORD`（若使用 Redis）
- `FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_REDIRECT_URI`（飞书登录与通讯录同步）
- `JWT_SECRET`、`JWT_EXPIRE`
- 可选：`HOST`（默认 0.0.0.0）、`PORT`（默认 9700）

环境文件：`.env.example` 为模板；`.env.dev`、`.env.prod` 为开发/生产预设（可提交），未设置 `ENV` 时可复制其一为 `.env` 或通过 `ENV=dev` 指定加载。

### LyEdu 配置模板（~/.lyedu/conf）

程序优先使用 `~/.lyedu/conf/config.ini` 中的 MySQL/Redis 配置；若不存在则自动在 `~/.lyedu/conf` 下生成 `config.ini.template` 模板。适合打包为可执行文件后交付：用户无需接触项目目录，只需在用户目录下配置即可。

**首次使用步骤：**

1. 运行程序后，若未找到 `config.ini`，会自动创建 `~/.lyedu/conf` 并生成 `config.ini.template`
2. 复制模板为实际配置：

   ```powershell
   # Windows（PowerShell 或 CMD）
   copy "%USERPROFILE%\.lyedu\conf\config.ini.template" "%USERPROFILE%\.lyedu\conf\config.ini"
   ```

   ```bash
   # Linux / macOS
   cp ~/.lyedu/conf/config.ini.template ~/.lyedu/conf/config.ini
   ```

3. 编辑 `config.ini` 填写 MySQL/Redis 信息
4. 重新运行程序

**说明：**

- `~/.lyedu` 为隐藏目录：Windows 需在「查看」→「隐藏的项目」中显示
- 若项目目录有 `.env` 或 `.env.dev`，在无 `config.ini` 时仍可使用 .env 继续运行（开发模式）

启动（应用启动时会自动执行 Alembic 迁移；迁移失败仅打日志，不阻塞服务）：

```bash
ENV=dev uvicorn main:app --host 0.0.0.0 --port 9700
```

或使用脚本：`.\start.ps1`（PowerShell）/ `./start.sh`（Linux/macOS）；脚本会按环境变量 `ENV` 或交互选择加载配置。

接口文档：<http://localhost:9700/docs>

## 已实现接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `POST /auth/login` | 登录，返回 token 与 userInfo |
| 课程 | `GET /course/page` | 分页列表 |
| 课程 | `GET /course/{id}` | 课程详情（含章节、视频、附件、学习记录与进度） |
| 课程 | `GET /course/recommended` | 推荐课程 |
| 课程 | `POST/PUT/DELETE /course` | 创建/更新/删除课程 |
| 章节 | `GET /chapter?courseId=` | 按课程查章节 |
| 章节 | `POST/PUT/DELETE /chapter` | 创建/更新/删除章节 |
| 视频 | `GET /video/page`、`/video/{id}`、`/video/course/{id}`、`/video/chapter/{id}` | 分页、详情、按课程/章节列表 |
| 视频 | `POST/PUT/DELETE /video` | 创建/更新/删除视频 |
| 学习 | `POST /learning/join` | 加入课程 |
| 学习 | `GET /learning/my-courses` | 我的课程 |
| 学习 | `POST /learning/video-progress` | 上报视频学习进度 |
| 学习 | `POST /learning/play-ping` | 播放心跳 |
| 学习 | `GET /learning/video-progress/{videoId}` | 获取视频进度 |
| 学习 | `GET /learning/watched-courses` | 已观看课程（含进度） |
| 用户 | `GET /user/page`、`GET /user/{id}` | 分页、详情 |
| 用户 | `POST/PUT/DELETE /user` | 创建/更新/删除用户 |
| 用户 | `POST /user/{id}/reset-password` | 重置密码 |

需登录的接口在请求头中携带：`Authorization: Bearer <token>`。

## 项目结构

```
lyedu-api-python/
  main.py           # 入口，挂载路由与 CORS
  config.py         # 配置（优先 ~/.lyedu/conf/config.ini，否则 .env）
  lyedu_config.py   # LyEdu 配置模板生成与加载（config.ini.template）
  db.py             # MySQL 连接与 query/execute
  common/result.py  # 统一响应 Result/ResultCode
  models/schemas.py # 请求体 Pydantic 模型
  services/         # 业务逻辑，按域分目录
  │   ├── auth/         # 登录日志
  │   ├── certificate/  # 证书与模板
  │   ├── content/      # 视频、图片、知识库
  │   ├── course/       # 课程、章节、附件、评论等
  │   ├── exam/         # 考试、试卷、试题、考试记录
  │   ├── learning/     # 积分、任务、标签
  │   ├── org/          # 部门
  │   ├── sync/         # 第三方通讯录同步（飞书/钉钉/企微）
  │   ├── system/       # 配置、上传
  │   └── user/         # 用户、学习记录等
  routers/          # FastAPI 路由（auth/course/chapter/video/learning/user 等）
  util/             # JWT、飞书 API 等
  .env.example      # 环境变量模板
  .env.dev / .env.prod  # 开发/生产环境预设
  requirements.txt
  README.md
```

## 打包与交付

程序可打包为单文件可执行，便于部署，无需安装 Python。

| 平台   | 产出              | 构建方式 |
|--------|-------------------|----------|
| Windows | `dist/lyedu_backend.exe` | 本地执行 `python -m PyInstaller lyedu_backend.spec` |
| Linux   | `dist/lyedu_backend`     | 在仓库根目录执行 `.\lyedu-api-python\build.ps1`（通过 Docker 跨平台构建） |

**Linux 打包说明：**

- 需安装 Docker；在 Windows 下可通过 Docker 模拟 Linux 环境完成打包。
- 产出为 `lyedu-api-python/dist/lyedu_backend`，拷贝到 Linux 主机后执行：`chmod +x lyedu_backend && ./lyedu_backend`，功能与 exe 相同。
- 国内网络访问 Docker Hub / PyPI 较慢时，可设置环境变量使用镜像：

  ```powershell
  $env:DOCKER_REGISTRY = "docker.m.daocloud.io/library/"   # Docker 镜像
  $env:PIP_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"  # PyPI 镜像
  .\lyedu-api-python\build.ps1
  ```

## 与 Java 版对照

- 数据库表、字段与 Java 版一致，可直接共用 MySQL。
- 响应格式：`{ code, message, data, timestamp }`，与 Java `Result` 一致。
- 分页：`PageResult` 含 `records`、`total`、`current`、`size`、`pages`。
