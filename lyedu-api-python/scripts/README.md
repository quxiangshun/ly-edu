# 脚本说明

## generate_demo_data.py — 全表 Demo 数据

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

## seed_questions.py — 试题种子数据

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

## sync_fa_to_ly.py — FA 数据同步到 LyEdu

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
