# 脚本说明

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
