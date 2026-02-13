# scripts — 脚本与配置目录

本目录按**使用场景**组织脚本和配置，同一场景下的文件放在同一子目录中，便于查找和引用（允许与根目录文件冗余）。

---

## 目录说明

| 目录 | 作用 |
|------|------|
| **dev/** | 本地开发环境一键启动/停止，与 `dev-config.yml` 搭配使用（支持 .yml，无则回退 .json） |
| **docker/** | Docker 部署：`.env` 与 `compose.yml` 组合使用，在此目录内执行 compose |

---

## dev/ — 开发环境一键启动

**用途**：在项目根目录外或任意位置，通过脚本按配置启动/停止本地开发服务（Python API、管理后台、PC 端等），并可选启动 Docker 中的 MySQL+Redis。

| 文件 | 作用 |
|------|------|
| **start.ps1** | 读取 `dev-config.yml`（无则 `dev-config.json`），按配置初始化环境（虚拟环境、npm install、Docker MySQL+Redis），在新终端中启动各服务；将终端 PID 写入仓库根目录 `.dev-servers.json` |
| **stop.ps1** | 根据 `.dev-servers.json` 关闭由 start 打开的终端，并结束占用 9700/9800/9900 端口的进程 |
| **dev-config.yml** | 当前使用的配置（YAML，可写注释）：`database`、`redis` 连接信息及用途说明；`start_docker_mysql_redis`、`start_lyedu_api`、`start_lyedu_api_python`、`start_lyedu_admin`、`start_lyedu_pc` 等开关。说明见文件内注释 |
| **dev-config.example.yml** | 配置示例，可复制为 `dev-config.yml` 后修改 |
| **dev-config.json** / **dev-config.example.json** | 仍支持，当不存在 `dev-config.yml` 时使用 |

**使用方式**（在仓库根目录执行）：

```powershell
.\scripts\dev\start.ps1   # 启动
.\scripts\dev\stop.ps1    # 停止
```

**说明**：脚本内部会解析仓库根目录（`scripts` 的上一级），所有子项目路径（如 `lyedu-api-python`、`lyedu-admin`）均相对于仓库根目录。启动 Docker MySQL+Redis 时使用本目录同级的 `scripts/docker/compose-mysql-redis.yml`。

---

## docker/ — Docker 部署（.env + compose 组合）

**用途**：将 Docker 部署所需的 `.env` 与 compose 文件放在同一目录，在此目录下执行 `docker compose` 时自动加载本目录的 `.env`，引用关系清晰。

| 文件 | 作用 |
|------|------|
| **.env.example** | 环境变量示例，供 Docker Compose 使用。主要变量：`DOCKER_REGISTRY`（镜像前缀）、`NPM_REGISTRY`（前端构建时的 npm 源）。复制为 `.env` 后按需修改 |
| **compose.yml** | 完整编排：MySQL + Redis + Java API + admin + pc。构建上下文与卷路径已按从本目录出发的 `../../` 书写，需在 **scripts/docker** 目录下执行 |
| **compose-mysql-redis.yml** | 仅 MySQL + Redis，供本地开发直连。同样需在 **scripts/docker** 目录下执行 |

**使用方式**：

```powershell
cd scripts\docker
copy .env.example .env
# 按需编辑 .env（如 DOCKER_REGISTRY、NPM_REGISTRY）
docker compose -f compose-mysql-redis.yml up -d   # 仅数据库
# 或
docker compose up -d   # 完整服务（需先构建 API jar 等）
```

**路径说明**：compose 内相对路径（如 `../../lyedu-admin`、`../../uploads`）均相对于 **scripts/docker**，因此必须在 `scripts/docker` 下执行 `docker compose`，与根目录下的 compose 可并存（根目录保留一份便于兼容旧用法）。
