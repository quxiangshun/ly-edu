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
