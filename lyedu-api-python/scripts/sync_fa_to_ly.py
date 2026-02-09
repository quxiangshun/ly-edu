# -*- coding: utf-8 -*-
"""
FA 数据同步到 LyEdu（fa_* @ localhost:3307 -> ly_* @ localhost:3306）

数据源：localhost:3307，库 xjty，用户 root/root
目标：  localhost:3306，库 lyedu，用户 root/lyedu123456

前置：目标库已执行 Alembic 至 v6（含 ly_user v5 字段、ly_video.description、ly_department.avatar/description/old_id/old_source）。仅做数据同步，不修改表结构。

在 lyedu-api-python 目录下执行：python scripts/sync_fa_to_ly.py
"""
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymysql
import bcrypt

# 源库（fa 数据）
SOURCE = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "root",
    "database": "xjty",
    "charset": "utf8mb4",
}
# 目标库（ly 数据）
TARGET = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "lyedu123456",
    "database": "lyedu",
    "charset": "utf8mb4",
}


def get_conn(config):
    return pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        charset=config["charset"],
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )


def check_target_schema(tgt):
    """确认目标库已执行 Alembic 至 v6（ly_user/ly_video v5 字段，ly_department v6 字段）。"""
    required = {
        "ly_user": ["nickname", "last_login_time", "study_time_long"],
        "ly_video": ["description"],
        "ly_department": ["avatar", "description", "old_id", "old_source"],
    }
    with tgt.cursor() as c:
        for table, columns in required.items():
            c.execute(f"SHOW COLUMNS FROM {table}")
            names = {(row.get("Field") or row.get("field") or "").lower() for row in c.fetchall()}
            for col in columns:
                if col.lower() not in names:
                    raise RuntimeError(
                        f"目标表 {table} 缺少字段 {col}，请先执行 Alembic 至 v6：cd lyedu-api-python && python -m alembic upgrade head"
                    )


def _hash_password(plain: str) -> str:
    """明文转 bcrypt 密文，与 ly 登录校验兼容；超过 72 字节则截断（bcrypt 限制）。"""
    raw = (plain or "123456").strip().encode("utf-8")[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("ascii")


def sync_staff_to_user(src, tgt):
    """1. fa_staff -> ly_user: account->username, name->nickname, password 明文转 bcrypt, 其余按字段映射"""
    with src.cursor() as c:
        c.execute(
            "SELECT id, account, name, password, phonenumber, avatar, openid, last_login_time, studytimelong, is_active FROM fa_staff"
        )
        rows = c.fetchall()
    if not rows:
        print("  fa_staff: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for i, r in enumerate(rows):
            if (i + 1) % 100 == 0 or i == 0:
                print(f"    fa_staff -> ly_user: {i + 1}/{len(rows)} ...")
            pwd = _hash_password(r.get("password") or "")
            username = (r.get("account") or "").strip() or f"user_{r['id']}"
            nickname = (r.get("name") or "").strip() or None
            c.execute(
                """INSERT INTO ly_user (id, username, nickname, password, mobile, avatar, union_id, last_login_time, study_time_long, status, role, deleted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'student', 0)
                ON DUPLICATE KEY UPDATE
                username=VALUES(username), nickname=VALUES(nickname), password=VALUES(password),
                mobile=VALUES(mobile), avatar=VALUES(avatar), union_id=VALUES(union_id), last_login_time=VALUES(last_login_time),
                study_time_long=VALUES(study_time_long), status=VALUES(status)""",
                (
                    r["id"],
                    username,
                    nickname,
                    pwd,
                    r.get("phonenumber") or None,
                    r.get("avatar") or None,
                    r.get("openid") or None,
                    r.get("last_login_time"),
                    r.get("studytimelong") or 0,
                    1 if (r.get("is_active") is None or r.get("is_active") != 0) else 0,
                ),
            )
    print(f"  fa_staff -> ly_user: {len(rows)} rows")


def sync_videocategory_to_tag(src, tgt):
    """2. fa_videocategory -> ly_tag"""
    with src.cursor() as c:
        c.execute("SELECT id, name, create_time, weigh FROM fa_videocategory")
        rows = c.fetchall()
    if not rows:
        print("  fa_videocategory: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            c.execute(
                """INSERT INTO ly_tag (id, name, create_time, sort) VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), create_time=VALUES(create_time), sort=VALUES(sort)""",
                (r["id"], r["name"], r.get("create_time"), r.get("weigh") or 0),
            )
    print(f"  fa_videocategory -> ly_tag: {len(rows)} rows")


def sync_course(src, tgt):
    """3. fa_course -> ly_course（其他字段默认）"""
    with src.cursor() as c:
        c.execute("SELECT id, name, create_time FROM fa_course")
        rows = c.fetchall()
    if not rows:
        print("  fa_course: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            c.execute(
                """INSERT INTO ly_course (id, title, create_time, status, sort, deleted) VALUES (%s, %s, %s, 1, 0, 0)
                ON DUPLICATE KEY UPDATE title=VALUES(title), create_time=VALUES(create_time)""",
                (r["id"], r["name"], r.get("create_time")),
            )
    print(f"  fa_course -> ly_course: {len(rows)} rows")


def sync_course_tag(src, tgt):
    """4. ly_course_tag：fa_course.id + fa_course.videocategory_id -> course_id, tag_id"""
    with src.cursor() as c:
        c.execute("SELECT id, videocategory_id FROM fa_course WHERE videocategory_id IS NOT NULL AND videocategory_id != ''")
        rows = c.fetchall()
    if not rows:
        print("  ly_course_tag: 0 rows, skip")
        return
    with tgt.cursor() as c:
        n = 0
        for r in rows:
            try:
                tag_id = int(r["videocategory_id"])
            except (TypeError, ValueError):
                continue
            c.execute(
                "INSERT IGNORE INTO ly_course_tag (course_id, tag_id) VALUES (%s, %s)",
                (r["id"], tag_id),
            )
            if c.rowcount:
                n += 1
    print(f"  ly_course_tag: {n} rows")


def sync_video(src, tgt):
    """5. fa_video -> ly_video（name->title, description, views->play_count, like/likes->like_count）"""
    with src.cursor() as c:
        c.execute("SELECT * FROM fa_video")
        rows = c.fetchall()
    if not rows:
        print("  fa_video: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            like_count = r.get("like") if r.get("like") is not None else r.get("likes")
            if like_count is None:
                like_count = 0
            c.execute(
                """INSERT INTO ly_video (id, course_id, chapter_id, title, url, cover, description, duration, sort, play_count, like_count, create_time, deleted)
                VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, 0, %s, %s, %s, 0)
                ON DUPLICATE KEY UPDATE title=VALUES(title), url=VALUES(url), cover=VALUES(cover), description=VALUES(description),
                duration=VALUES(duration), play_count=VALUES(play_count), like_count=VALUES(like_count), create_time=VALUES(create_time)""",
                (
                    r["id"],
                    r.get("course_id") or 0,
                    r.get("name") or "",
                    r.get("url") or "",
                    r.get("cover_image") or None,
                    r.get("description") or None,
                    r.get("duration") or 0,
                    r.get("views") or 0,
                    like_count,
                    r.get("create_time"),
                ),
            )
    print(f"  fa_video -> ly_video: {len(rows)} rows")


def _norm_answer(question_type: str, answer: str) -> str:
    if not answer:
        return ""
    if (question_type or "").strip().lower() == "multiple":
        return (answer or "").replace(",", "").strip()
    return (answer or "").strip()


def sync_question(src, tgt):
    """6. fa_question -> ly_question（option_a/b/c/d -> options JSON, question_type: multiple->multi, answer 多选去逗号）"""
    with src.cursor() as c:
        c.execute(
            "SELECT id, name, option_a, option_b, option_c, option_d, question_type, answer, analysis, create_time FROM fa_question"
        )
        rows = c.fetchall()
    if not rows:
        print("  fa_question: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            qtype = (r.get("question_type") or "single").strip().lower()
            if qtype == "multiple":
                qtype = "multi"
            elif qtype != "single":
                qtype = "single"
            options = json.dumps(
                [
                    (r.get("option_a") or "").strip(),
                    (r.get("option_b") or "").strip(),
                    (r.get("option_c") or "").strip(),
                    (r.get("option_d") or "").strip(),
                ],
                ensure_ascii=False,
            )
            answer = _norm_answer(r.get("question_type"), r.get("answer") or "")
            c.execute(
                """INSERT INTO ly_question (id, type, title, options, answer, score, analysis, sort, create_time, deleted)
                VALUES (%s, %s, %s, %s, %s, 10, %s, 0, %s, 0)
                ON DUPLICATE KEY UPDATE type=VALUES(type), title=VALUES(title), options=VALUES(options), answer=VALUES(answer), analysis=VALUES(analysis), create_time=VALUES(create_time)""",
                (
                    r["id"],
                    qtype,
                    (r.get("name") or "").strip(),
                    options,
                    answer,
                    (r.get("analysis") or "").strip() or None,
                    r.get("create_time"),
                ),
            )
    print(f"  fa_question -> ly_question: {len(rows)} rows")


def sync_exam_to_paper(src, tgt):
    """7. fa_exam -> ly_paper（status=1, total_score=100, create_time->update_time）"""
    with src.cursor() as c:
        c.execute("SELECT id, name, passscore, duration, create_time FROM fa_exam")
        rows = c.fetchall()
    if not rows:
        print("  fa_exam: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            c.execute(
                """INSERT INTO ly_paper (id, title, total_score, pass_score, duration_minutes, status, create_time, update_time, deleted)
                VALUES (%s, %s, 100, %s, %s, 1, %s, %s, 0)
                ON DUPLICATE KEY UPDATE title=VALUES(title), pass_score=VALUES(pass_score), duration_minutes=VALUES(duration_minutes), update_time=VALUES(update_time)""",
                (
                    r["id"],
                    r.get("name") or "",
                    r.get("passscore") or 60,
                    r.get("duration") or 60,
                    r.get("create_time"),
                    r.get("create_time"),
                ),
            )
    print(f"  fa_exam -> ly_paper: {len(rows)} rows")


def sync_paper_question(src, tgt):
    """8. ly_paper_question: fa_paperinfo.exam_id->paper_id, question_list 元素->question_id, score=1"""
    with src.cursor() as c:
        c.execute("SELECT exam_id, question_list FROM fa_paperinfo WHERE question_list IS NOT NULL AND question_list != ''")
        rows = c.fetchall()
    seen = set()
    to_insert = []
    for r in rows:
        paper_id = r["exam_id"]
        try:
            qlist = json.loads(r["question_list"]) if isinstance(r["question_list"], str) else r["question_list"]
        except Exception:
            continue
        if not isinstance(qlist, list):
            continue
        for sort, qid in enumerate(qlist):
            try:
                qid = int(qid)
            except (TypeError, ValueError):
                continue
            key = (paper_id, qid)
            if key in seen:
                continue
            seen.add(key)
            to_insert.append((paper_id, qid, 1, sort))
    if not to_insert:
        print("  ly_paper_question: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for paper_id, question_id, score, sort in to_insert:
            c.execute(
                "INSERT IGNORE INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (%s, %s, %s, %s)",
                (paper_id, question_id, score, sort),
            )
    print(f"  ly_paper_question: {len(to_insert)} rows")


def sync_paper_to_exam(src, tgt):
    """9. fa_paper -> ly_exam（paper_id=exam_id, 标题等来自 fa_exam）"""
    with src.cursor() as c:
        c.execute(
            """SELECT p.id, p.exam_id, p.start_time, p.submit_time, e.name AS title, e.duration, e.passscore
             FROM fa_paper p
             LEFT JOIN fa_exam e ON e.id = p.exam_id"""
        )
        rows = c.fetchall()
    if not rows:
        print("  fa_paper -> ly_exam: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            c.execute(
                """INSERT INTO ly_exam (id, title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status, create_time, update_time, deleted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 1, %s, %s, 0)
                ON DUPLICATE KEY UPDATE title=VALUES(title), paper_id=VALUES(paper_id), start_time=VALUES(start_time), end_time=VALUES(end_time),
                duration_minutes=VALUES(duration_minutes), pass_score=VALUES(pass_score), update_time=VALUES(update_time)""",
                (
                    r["id"],
                    r.get("title") or "",
                    r.get("exam_id"),
                    r.get("start_time"),
                    r.get("submit_time"),
                    r.get("duration") or 60,
                    r.get("passscore") or 60,
                    r.get("start_time"),
                    r.get("submit_time") or r.get("start_time"),
                ),
            )
    print(f"  fa_paper -> ly_exam: {len(rows)} rows")


def sync_team_to_department(src, tgt):
    """9. fa_team -> ly_department：id->id, name->name, info->description, create_time, id->old_id(t_id), old_source='team'"""
    with src.cursor() as c:
        c.execute("SELECT * FROM fa_team")
        rows = c.fetchall()
    if not rows:
        print("  fa_team: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            rid = r.get("id")
            name = (r.get("name") or "").strip() or "-"
            desc = r.get("info") or r.get("description")
            ct = r.get("create_time")
            avatar = r.get("avatar")
            c.execute(
                """INSERT INTO ly_department (id, name, parent_id, sort, status, avatar, description, create_time, update_time, old_id, old_source, deleted)
                VALUES (%s, %s, 0, 0, 1, %s, %s, %s, %s, %s, 'team', 0)
                ON DUPLICATE KEY UPDATE name=VALUES(name), avatar=VALUES(avatar), description=VALUES(description), create_time=VALUES(create_time), update_time=VALUES(update_time), old_id=VALUES(old_id), old_source=VALUES(old_source)""",
                (rid, name, avatar, desc, ct, ct, rid),
            )
    print(f"  fa_team -> ly_department: {len(rows)} rows")


def sync_group_to_department(src, tgt):
    """10. fa_group -> ly_department：id 自增，name->name, info->description, create_time, id->old_id(g_id), old_source='group'；team_id->parent_id（对应 ly_department 中 fa_team 的 id）"""
    with src.cursor() as c:
        c.execute("SELECT * FROM fa_group")
        rows = c.fetchall()
    if not rows:
        print("  fa_group: 0 rows, skip")
        return
    with tgt.cursor() as c:
        for r in rows:
            name = (r.get("name") or "").strip() or "-"
            desc = r.get("info") or r.get("description")
            ct = r.get("create_time")
            old_id = r.get("id")
            parent_id = r.get("team_id") if r.get("team_id") is not None else 0
            c.execute(
                """INSERT INTO ly_department (name, parent_id, sort, status, avatar, description, create_time, update_time, old_id, old_source, deleted)
                VALUES (%s, %s, 0, 1, NULL, %s, %s, %s, %s, 'group', 0)""",
                (name, parent_id, desc, ct, ct, old_id),
            )
    print(f"  fa_group -> ly_department: {len(rows)} rows")


def sync_staffgroup_to_user_department(src, tgt):
    """11. fa_staffgroup -> ly_user.department_id：按 staff_id=ly_user.id，用 group_id 查 ly_department(old_source='group',old_id=group_id) 的 id 写入 department_id"""
    with src.cursor() as c:
        c.execute("SELECT staff_id, group_id FROM fa_staffgroup")
        rows = c.fetchall()
    if not rows:
        print("  fa_staffgroup -> ly_user.department_id: 0 rows, skip")
        return
    with tgt.cursor() as c:
        dept_map = {}
        updated = 0
        for r in rows:
            staff_id = r.get("staff_id")
            group_id = r.get("group_id")
            if staff_id is None or group_id is None:
                continue
            if group_id not in dept_map:
                c.execute(
                    "SELECT id FROM ly_department WHERE old_source = 'group' AND old_id = %s AND deleted = 0 LIMIT 1",
                    (group_id,),
                )
                row = c.fetchone()
                dept_map[group_id] = row["id"] if row else None
            dept_id = dept_map[group_id]
            if dept_id is None:
                continue
            c.execute("UPDATE ly_user SET department_id = %s WHERE id = %s AND deleted = 0", (dept_id, staff_id))
            if c.rowcount:
                updated += 1
    print(f"  fa_staffgroup -> ly_user.department_id: {updated} updated")


def sync_teamcourse_to_course_department(src, tgt):
    """12. fa_teamcourse -> ly_course_department：team_id->department_id, course_id->course_id"""
    with src.cursor() as c:
        c.execute("SELECT team_id, course_id FROM fa_teamcourse")
        rows = c.fetchall()
    if not rows:
        print("  fa_teamcourse -> ly_course_department: 0 rows, skip")
        return
    with tgt.cursor() as c:
        n = 0
        for r in rows:
            c.execute(
                "INSERT IGNORE INTO ly_course_department (course_id, department_id) VALUES (%s, %s)",
                (r["course_id"], r["team_id"]),
            )
            if c.rowcount:
                n += 1
    print(f"  fa_teamcourse -> ly_course_department: {n} rows")


def main():
    print("Sync FA (3307/xjty) -> Ly (3306/lyedu)")
    src = get_conn(SOURCE)
    tgt = get_conn(TARGET)
    try:
        check_target_schema(tgt)
        sync_staff_to_user(src, tgt)
        sync_team_to_department(src, tgt)
        sync_group_to_department(src, tgt)
        sync_staffgroup_to_user_department(src, tgt)
        sync_videocategory_to_tag(src, tgt)
        sync_course(src, tgt)
        sync_course_tag(src, tgt)
        sync_teamcourse_to_course_department(src, tgt)
        sync_video(src, tgt)
        sync_question(src, tgt)
        sync_exam_to_paper(src, tgt)
        sync_paper_question(src, tgt)
        sync_paper_to_exam(src, tgt)
        tgt.commit()
        print("Done.")
    except Exception as e:
        tgt.rollback()
        print(f"Error: {e}")
        traceback.print_exc()
        raise
    finally:
        src.close()
        tgt.close()


if __name__ == "__main__":
    main()
