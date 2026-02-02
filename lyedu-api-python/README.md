# LyEdu API - Python 版本

与 LyEdu Java (Spring Boot) 后台功能对应的 Python 实现，使用 **FastAPI** + **PyMySQL**，本地 Python 建议 **3.14.2**（兼容 3.10+）。

## 环境

- Python 3.10+（推荐 3.14.2）
- MySQL（与 Java 版共用同一数据库）

## 安装与运行

**请在终端（命令提示符或 PowerShell）里执行以下命令，不要用“打开文件”的方式运行。**

1. 进入项目目录，用 **python -m** 创建虚拟环境（使用 `venv` 目录名）：

```bash
cd lyedu-api-python
python -m venv venv
```

若本机只有 `py` 启动器，可用：`py -3 -m venv venv`。

2. 激活虚拟环境：

- **Windows 命令提示符：** `venv\Scripts\activate.bat`
- **Windows PowerShell：** `venv\Scripts\Activate.ps1`
- **Linux/macOS：** `source venv/bin/activate`

3. 安装依赖（建议使用国内镜像，见下方）：

```bash
pip install -r requirements.txt
```

4. 启动服务（**启动时会自动执行 Alembic 迁移**）：

```bash
uvicorn main:app --host 0.0.0.0 --port 9700
```

或使用启动脚本（先执行 `alembic upgrade head`，再启动 uvicorn）：

- **PowerShell：** `.\start.ps1`
- **Linux/macOS：** `./start.sh`（需 `chmod +x start.sh`）

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

**方式三：一键脚本（创建 venv + 用清华源安装）**

- PowerShell：`.\install.ps1`
- 命令提示符：`install.bat`

配置环境变量（或使用项目根目录 `.env`）：

- `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USERNAME`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`
- `JWT_SECRET`、`JWT_EXPIRE`
- 可选：`HOST`（默认 0.0.0.0）、`PORT`（默认 9700）

启动（应用启动时会自动执行 Alembic 迁移；迁移失败仅打日志，不阻塞服务）：

```bash
uvicorn main:app --host 0.0.0.0 --port 9700
```

或使用脚本：`.\start.ps1`（PowerShell）/ `./start.sh`（Linux/macOS）。

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
  config.py         # 配置（环境变量）
  db.py             # MySQL 连接与 query/execute
  common/result.py  # 统一响应 Result/ResultCode
  models/schemas.py # 请求体 Pydantic 模型
  services/         # 业务逻辑（course/chapter/video/user/learning）
  routers/          # FastAPI 路由（auth/course/chapter/video/learning/user）
  util/jwt_util.py  # JWT 生成与解析
  requirements.txt
  README.md
```

## 与 Java 版对照

- 数据库表、字段与 Java 版一致，可直接共用 MySQL。
- 响应格式：`{ code, message, data, timestamp }`，与 Java `Result` 一致。
- 分页：`PageResult` 含 `records`、`total`、`current`、`size`、`pages`。
