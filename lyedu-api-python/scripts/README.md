# lyedu-api-python 脚本说明

本文档说明 **lyedu-api-python** 目录下所有脚本的依赖关系与作用（根目录脚本 + `scripts/` 下 Python 脚本）。

---

## 一、脚本分布与依赖关系

### 1.1 脚本位置

| 位置 | 脚本 | 作用 |
|------|------|------|
| **根目录** | `start.ps1` | Windows：激活 .venv → Alembic 迁移 → 启动 uvicorn |
| **根目录** | `start.sh` | Linux/Mac：同上 |
| **根目录** | `install.ps1` | Windows：创建 venv、用清华源安装 requirements.txt |
| **根目录** | `_start_runner.ps1` | 由仓库根 `scripts/dev/start.ps1` **动态生成**，写入 DB/Redis 等环境变量后执行迁移 + uvicorn |
| **根目录** | `docker-entrypoint.sh` | Docker 容器入口：等 MySQL 就绪 → Alembic 迁移 → uvicorn |
| **scripts/** | `generate_demo_data.py` | 插入全表 demo 数据 |
| **scripts/** | `seed_questions.py` | 插入试题种子数据 |
| **scripts/** | `sync_fa_to_ly.py` | 将 FA 系统数据同步到 LyEdu |

### 1.2 依赖关系（谁依赖谁）

```
环境/依赖
  ├── Python 3.10+、pip、requirements.txt
  ├── MySQL 已启动且与 .env / config 一致
  └── （可选）Redis

install.ps1
  └── 依赖：python、requirements.txt
  └── 产出：venv/（注意与 .venv 不同，根目录 start 系列使用 .venv）

start.ps1 / start.sh
  └── 依赖：.venv 已存在、alembic、uvicorn、config/.env
  └── 不创建 .venv，仅激活后执行迁移 + 启动

_start_runner.ps1
  └── 由 仓库根 scripts/dev/start.ps1 按 dev-config.json 生成
  └── 依赖：.venv、alembic、uvicorn
  └── 环境变量由生成方注入（MYSQL_*、REDIS_*、ENV 等）

docker-entrypoint.sh
  └── 依赖：镜像内已 pip install、环境变量 MYSQL_* 等由 Docker 传入
  └── 行为：等 MySQL → alembic upgrade head → uvicorn

scripts/*.py（generate_demo_data、seed_questions、sync_fa_to_ly）
  └── 依赖：项目根 config.py / .env、已安装项目依赖（如 pymysql、openpyxl 等）
  └── 建议在 lyedu-api-python 目录下、激活 .venv 后执行
```

### 1.3 推荐使用顺序（本地开发）

1. **首次**：创建虚拟环境并安装依赖  
   - Windows：在 lyedu-api-python 下执行 `python -m venv .venv`，再 `.\.venv\Scripts\pip.exe install -r requirements.txt`  
   - 或使用仓库根一键启动：`.\scripts\dev\start.ps1`（会检查并创建 .venv、补全依赖后生成并运行 _start_runner.ps1）
2. **日常启动 API**：  
   - 方式 A：在 lyedu-api-python 下执行 `.\start.ps1` 或 `./start.sh`  
   - 方式 B：在仓库根执行 `.\scripts\dev\start.ps1`（会启动 Python API 等多项服务）
3. **数据/种子**：先 `alembic upgrade head`，再按需运行 `scripts/generate_demo_data.py`、`scripts/seed_questions.py` 或 `scripts/sync_fa_to_ly.py`。

---

## 二、根目录脚本简要说明

| 脚本 | 作用 | 依赖 |
|------|------|------|
| **start.ps1** | Windows 下在本目录执行：设置 PYTHONUTF8；若存在 .venv 则激活；执行 `alembic upgrade head`；启动 `uvicorn main:app`（HOST/PORT 从环境变量读，未设则 uvicorn 默认）。 | .venv（可选）、alembic、uvicorn、config/.env |
| **start.sh** | Linux/Mac 下同上：`alembic upgrade head` → `uvicorn main:app --reload`。 | 已安装依赖（alembic、uvicorn）、.env |
| **install.ps1** | 创建 **venv**（非 .venv）、用清华源 `pip install -r requirements.txt`。与根目录 start.ps1 使用的 .venv 可并存，若用 start.ps1 建议建 .venv。 | python、requirements.txt |
| **_start_runner.ps1** | 由仓库根 **scripts/dev/start.ps1** 按 dev-config.json 动态生成，写入 MYSQL_*、REDIS_*、ENV 等环境变量后激活 .venv、执行 alembic、启动 uvicorn。勿手动编辑。 | .venv、alembic、uvicorn |
| **docker-entrypoint.sh** | Docker 容器入口：循环检测 MySQL 可连后执行 `alembic upgrade head`，再 `uvicorn main:app`。 | 镜像内已安装依赖、环境变量 MYSQL_* 等 |

---

## 三、scripts/ 下脚本说明

### generate_demo_data.py — 全表 Demo 数据

为所有业务表各插入 **15 条** 关联 demo 数据，便于本地演示与联调。**不参与数据库版本控制**，可单独多次运行（注意：重复运行会因唯一键冲突报错，仅建议在空库或测试库执行一次）。

**依赖：** 需在已安装项目依赖的环境中运行（如 `pip install -r requirements.txt` 或使用项目虚拟环境）。

**推荐：先执行迁移再跑 demo**（若库由 Flyway 管理可跳过）：

```bash
# 在 lyedu-api-python 目录下
python -m alembic upgrade head
python scripts/generate_demo_data.py
```

**兼容：** 若未执行 Alembic v13（或 Flyway V14），`ly_video` 无 `play_count`/`like_count` 时脚本会自动用不含这两列的 INSERT；若表 `ly_video_like`、`ly_course_video`、`ly_course_exam` 不存在则会跳过对应插入并提示执行相应迁移。

插入顺序按外键依赖：部门、分类、用户、课程、章节、视频、试题、试卷、考试、证书、任务、评论、知识库、积分、文件等；演示用户密码与初始化一致（lyedu123456）。

---

### seed_questions.py — 试题种子数据

生成各类型试题并插入 `ly_question` 表。

**题型：**

- `single` 单选
- `multi` 多选
- `judge` 判断（答案填 T/F）
- `fill` 填空
- `short` 简答

**运行前：** 确保 MySQL 已启动，且与 `config.py` / `.env` 中配置一致。

**运行：** 在项目根目录 `lyedu-api-python` 下执行：

```bash
python scripts/seed_questions.py
```

脚本会向数据库插入约 14 道 **demo 题**（单选 3、多选 2、判断 3、填空 3、简答 2），可在后台「试题管理」中查看；正式环境请按业务自行维护试题。

---

### sync_fa_to_ly.py — FA 数据同步到 LyEdu

将原系统（FastAdmin / xjty_course）的 fa_* 表数据同步到 LyEdu 的 ly_* 表。

**数据源/目标：** 从 `.env` 或 config 读取（见 `.env.example` 中 `FA_SOURCE_*`、`FA_TARGET_*`）。默认：数据源 `127.0.0.1:3307/xjty`，目标复用 `MYSQL_*`（如 `localhost:3306/lyedu`）。

**前置：** 目标库需先执行 **db/alembic** 的 v6 迁移（含 ly_user v5 字段、ly_video.description、ly_department.avatar/description/old_id/old_source）。同步脚本只做数据同步，不修改表结构。

**映射概要：**

| 源表 / 源数据 | 目标表 | 说明 |
|---------------|--------|------|
| fa_staff | ly_user | id→id；account→username；name→nickname；password 明文→bcrypt；phonenumber→mobile；avatar/openid→union_id；last_login_time/studytimelong→study_time_long；is_active→status |
| fa_videocategory | ly_tag | id/name/create_time/weigh→sort |
| fa_course | ly_course | id/name→title/create_time，其余默认 |
| fa_course.id + videocategory_id | ly_course_tag | course_id, tag_id |
| fa_video | ly_video | id/name→title/description/views→play_count/like或likes→like_count/create_time/course_id，url/cover_image→cover/duration |
| fa_question | ly_question | id/name→title/option_a~d→options JSON/question_type(multiple→multi)/answer(多选去逗号)/analysis/create_time，score 默认 10 |
| fa_exam | ly_paper | id/name→title/passscore→pass_score/duration→duration_minutes，status=1，total_score=100，create_time→update_time |
| fa_paperinfo | ly_paper_question | exam_id→paper_id，question_list 数组元素→question_id，score=1（去重） |
| fa_paper + fa_exam | ly_exam | id/paper_id=exam_id/start_time/end_time=submit_time，title/duration_minutes/pass_score 来自 fa_exam |

**运行：** 在 `lyedu-api-python` 目录下执行：

```bash
python scripts/sync_fa_to_ly.py
```

脚本使用 `INSERT ... ON DUPLICATE KEY UPDATE` 或 `INSERT IGNORE`，可重复执行以增量更新；首次运行前请确保两库均可连通。
