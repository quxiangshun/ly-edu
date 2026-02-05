# -*- coding: utf-8 -*-
"""
生成所有表的 demo 数据（每表 15 条），可单独运行，不参与数据库版本控制。
在 lyedu-api-python 目录下执行：python scripts/generate_demo_data.py
"""
import hashlib
import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import db

# 与 V1 初始化一致，密码 lyedu123456
DEMO_PASSWORD_HASH = "$2a$10$YORpsv2uYZQNNt5hxVNrw.KyeVMcn.fjWYyX3CWGXSwdpL6hRpVSy"
N = 15


def insert_one(cur, sql, args):
    cur.execute(sql, args or ())
    return cur.lastrowid or 0


def main():
    conn = db.get_connection()
    cur = conn.cursor()
    ids = {}
    try:
        # 1. ly_department
        sql = "INSERT INTO ly_department (name, parent_id, sort, status) VALUES (%s, %s, %s, %s)"
        ids["department"] = []
        for i in range(1, N + 1):
            pid = ids["department"][-1] if ids["department"] else 0
            lid = insert_one(cur, sql, (f"演示部门{i}", pid, i, 1))
            ids["department"].append(lid)
        print("  ly_department: 15")

        # 2. ly_course_category
        sql = "INSERT INTO ly_course_category (name, parent_id, sort, status) VALUES (%s, %s, %s, %s)"
        ids["category"] = []
        for i in range(1, N + 1):
            pid = ids["category"][-1] if ids["category"] else 0
            lid = insert_one(cur, sql, (f"演示分类{i}", pid, i, 1))
            ids["category"].append(lid)
        print("  ly_course_category: 15")

        # 3. ly_config (config_key 唯一)
        sql = "INSERT INTO ly_config (config_key, config_value, category, remark) VALUES (%s, %s, %s, %s)"
        for i in range(1, N + 1):
            cur.execute(sql, (f"demo.config.key_{i}", f"value_{i}", "demo", f"演示配置{i}"))
        print("  ly_config: 15")

        # 4. ly_point_rule (rule_key 唯一)
        sql = "INSERT INTO ly_point_rule (rule_key, rule_name, points, enabled, remark) VALUES (%s, %s, %s, %s, %s)"
        ids["point_rule"] = []
        for i in range(1, N + 1):
            lid = insert_one(cur, sql, (f"demo_rule_{i}", f"演示规则{i}", 5 + i, 1, f"备注{i}"))
            ids["point_rule"].append(lid)
        print("  ly_point_rule: 15")

        # 5. ly_file_hash (content_hash 唯一)
        sql = "INSERT INTO ly_file_hash (content_hash, relative_path, file_size) VALUES (%s, %s, %s)"
        ids["file_hash"] = []
        for i in range(1, N + 1):
            h = hashlib.sha256(f"demo_file_{i}".encode()).hexdigest()
            lid = insert_one(cur, sql, (h, f"videos/demo/{i}/file.mp4", 1000 * i))
            ids["file_hash"].append(lid)
        print("  ly_file_hash: 15")

        # 6. ly_user（兼容有无 entry_date、open_id、total_points）
        ids["user"] = []
        sql_full = (
            "INSERT INTO ly_user (username, password, real_name, email, mobile, avatar, open_id, department_id, entry_date, total_points, role, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        args_full = [
            (
                f"demo{i}",
                DEMO_PASSWORD_HASH,
                f"演示用户{i}",
                f"demo{i}@lyedu.com",
                f"1380000{i:04d}",
                None,
                None,
                ids["department"][(i - 1) % N],
                (date.today() - timedelta(days=30 * i)).isoformat(),
                0,
                "student" if i > 1 else "admin",
                1,
            )
            for i in range(1, N + 1)
        ]
        sql_mini = (
            "INSERT INTO ly_user (username, password, real_name, email, mobile, department_id, role, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        args_mini = [
            (
                f"demo{i}",
                DEMO_PASSWORD_HASH,
                f"演示用户{i}",
                f"demo{i}@lyedu.com",
                f"1380000{i:04d}",
                ids["department"][(i - 1) % N],
                "student" if i > 1 else "admin",
                1,
            )
            for i in range(1, N + 1)
        ]
        try:
            for i in range(N):
                lid = insert_one(cur, sql_full, args_full[i])
                ids["user"].append(lid)
        except Exception as e:
            if "1054" in str(e) and ("entry_date" in str(e) or "open_id" in str(e) or "total_points" in str(e)):
                print(f"\n警告: 数据库缺少字段 entry_date/open_id/total_points，使用简化版本插入。")
                print("建议: 先执行 'python -m alembic upgrade head' 确保表结构完整后再运行此脚本。")
                ids["user"] = []
                for i in range(N):
                    lid = insert_one(cur, sql_mini, args_mini[i])
                    ids["user"].append(lid)
            else:
                raise
        print("  ly_user: 15")

        # 7. ly_course
        sql = (
            "INSERT INTO ly_course (title, cover, description, category_id, status, sort, is_required, visibility) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        ids["course"] = []
        for i in range(1, N + 1):
            cid = ids["category"][(i - 1) % N]
            lid = insert_one(
                cur,
                sql,
                (
                    f"演示课程{i}",
                    f"https://via.placeholder.com/300x200?text=Demo{i}",
                    f"演示课程{i}的描述内容",
                    cid,
                    1,
                    i,
                    i % 2,
                    1,
                ),
            )
            ids["course"].append(lid)
        print("  ly_course: 15")

        # 8. ly_course_department (uk course_id, department_id)
        sql = "INSERT INTO ly_course_department (course_id, department_id) VALUES (%s, %s)"
        for i in range(N):
            cur.execute(sql, (ids["course"][i], ids["department"][i]))
        print("  ly_course_department: 15")

        # 9. ly_course_chapter
        sql = "INSERT INTO ly_course_chapter (course_id, title, sort) VALUES (%s, %s, %s)"
        ids["chapter"] = []
        for i in range(N):
            lid = insert_one(cur, sql, (ids["course"][i], f"第1章 演示章节", 1))
            ids["chapter"].append(lid)
        print("  ly_course_chapter: 15")

        # 10. ly_course_attachment
        sql = "INSERT INTO ly_course_attachment (course_id, name, type, file_url, sort) VALUES (%s, %s, %s, %s, %s)"
        for i in range(N):
            cur.execute(
                sql,
                (ids["course"][i], f"演示附件{i}.pdf", "pdf", f"/files/demo/{i}.pdf", i),
            )
        print("  ly_course_attachment: 15")

        # 11. ly_video（兼容有无 play_count/like_count：先试带两列，失败则用不含两列的 INSERT）
        ids["video"] = []
        sql_full = (
            "INSERT INTO ly_video (course_id, chapter_id, title, url, cover, duration, sort, play_count, like_count) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        args_full = [
            (ids["course"][i], ids["chapter"][i], f"演示视频{i}", f"/uploads/videos/demo_{i}.mp4",
             f"/uploads/covers/demo_{i}.jpg", 120 + i * 30, i, i * 10, i * 2)
            for i in range(N)
        ]
        sql_mini = (
            "INSERT INTO ly_video (course_id, chapter_id, title, url, cover, duration, sort) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        args_mini = [
            (ids["course"][i], ids["chapter"][i], f"演示视频{i}", f"/uploads/videos/demo_{i}.mp4",
             f"/uploads/covers/demo_{i}.jpg", 120 + i * 30, i)
            for i in range(N)
        ]
        try:
            for i in range(N):
                lid = insert_one(cur, sql_full, args_full[i])
                ids["video"].append(lid)
        except Exception as e:
            if "1054" in str(e) and "play_count" in str(e):
                ids["video"] = []
                for i in range(N):
                    lid = insert_one(cur, sql_mini, args_mini[i])
                    ids["video"].append(lid)
            else:
                raise
        print("  ly_video: 15")

        # 12. ly_question
        sql = "INSERT INTO ly_question (type, title, options, answer, score, analysis, sort) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        ids["question"] = []
        for i in range(1, N + 1):
            opts = json.dumps([f"A选项{i}", f"B选项{i}", f"C选项{i}"], ensure_ascii=False)
            lid = insert_one(
                cur,
                sql,
                ("single", f"演示单选题{i}？", opts, "A", 10, f"解析{i}", i),
            )
            ids["question"].append(lid)
        print("  ly_question: 15")

        # 13. ly_paper
        sql = "INSERT INTO ly_paper (title, total_score, pass_score, duration_minutes, status) VALUES (%s, %s, %s, %s, %s)"
        ids["paper"] = []
        for i in range(1, N + 1):
            lid = insert_one(cur, sql, (f"演示试卷{i}", 100, 60, 60, 1))
            ids["paper"].append(lid)
        print("  ly_paper: 15")

        # 14. ly_paper_question (paper_id, question_id 唯一)
        sql = "INSERT INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (%s, %s, %s, %s)"
        for i in range(N):
            cur.execute(sql, (ids["paper"][i], ids["question"][i], 10, i))
        print("  ly_paper_question: 15")

        # 15. ly_exam
        sql = (
            "INSERT INTO ly_exam (title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        ids["exam"] = []
        base_time = datetime.now() - timedelta(days=7)
        for i in range(N):
            lid = insert_one(
                cur,
                sql,
                (
                    f"演示考试{i}",
                    ids["paper"][i],
                    base_time + timedelta(days=i),
                    base_time + timedelta(days=i, hours=2),
                    60,
                    60,
                    1,
                    1,
                ),
            )
            ids["exam"].append(lid)
        print("  ly_exam: 15")

        # 16. ly_exam_department
        sql = "INSERT INTO ly_exam_department (exam_id, department_id) VALUES (%s, %s)"
        for i in range(N):
            cur.execute(sql, (ids["exam"][i], ids["department"][i]))
        print("  ly_exam_department: 15")

        # 17. ly_exam_record
        sql = (
            "INSERT INTO ly_exam_record (exam_id, user_id, paper_id, score, passed, answers, submit_time) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        for i in range(N):
            cur.execute(
                sql,
                (
                    ids["exam"][i],
                    ids["user"][i],
                    ids["paper"][i],
                    60 + i * 2,
                    1,
                    json.dumps({"q1": "A"}, ensure_ascii=False),
                    datetime.now() - timedelta(days=i),
                ),
            )
        print("  ly_exam_record: 15")

        # 18. ly_certificate_template
        sql = "INSERT INTO ly_certificate_template (name, description, config, sort, status) VALUES (%s, %s, %s, %s, %s)"
        ids["cert_template"] = []
        for i in range(1, N + 1):
            lid = insert_one(
                cur,
                sql,
                (f"演示证书模板{i}", f"说明{i}", "{}", i, 1),
            )
            ids["cert_template"].append(lid)
        print("  ly_certificate_template: 15")

        # 19. ly_certificate (template_id, source_type, source_id)
        sql = (
            "INSERT INTO ly_certificate (template_id, name, source_type, source_id, sort, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        ids["certificate"] = []
        for i in range(N):
            lid = insert_one(
                cur,
                sql,
                (
                    ids["cert_template"][i],
                    f"演示证书{i}",
                    "exam",
                    ids["exam"][i],
                    i,
                    1,
                ),
            )
            ids["certificate"].append(lid)
        print("  ly_certificate: 15")

        # 20. ly_user_certificate (certificate_no 唯一)
        sql = (
            "INSERT INTO ly_user_certificate (user_id, certificate_id, template_id, certificate_no, title, issued_at) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        for i in range(N):
            cur.execute(
                sql,
                (
                    ids["user"][i],
                    ids["certificate"][i],
                    ids["cert_template"][i],
                    f"DEMO-CERT-{ids['user'][i]}-{ids['certificate'][i]}",
                    f"演示证书{i}",
                    datetime.now() - timedelta(days=i),
                ),
            )
        print("  ly_user_certificate: 15")

        # 21. ly_task (certificate_id 可空)
        sql = (
            "INSERT INTO ly_task (title, description, cycle_type, cycle_config, items, certificate_id, sort, status, start_time, end_time) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        ids["task"] = []
        items = json.dumps([{"type": "course", "id": ids["course"][0]}, {"type": "exam", "id": ids["exam"][0]}], ensure_ascii=False)
        for i in range(1, N + 1):
            lid = insert_one(
                cur,
                sql,
                (
                    f"演示任务{i}",
                    f"任务说明{i}",
                    "once",
                    "{}",
                    items,
                    ids["certificate"][(i - 1) % N] if i <= N else None,
                    i,
                    1,
                    datetime.now() - timedelta(days=30),
                    datetime.now() + timedelta(days=30),
                ),
            )
            ids["task"].append(lid)
        print("  ly_task: 15")

        # 22. ly_task_department
        sql = "INSERT INTO ly_task_department (task_id, department_id) VALUES (%s, %s)"
        for i in range(N):
            cur.execute(sql, (ids["task"][i], ids["department"][i]))
        print("  ly_task_department: 15")

        # 23. ly_user_task (uk user_id, task_id)
        sql = "INSERT INTO ly_user_task (user_id, task_id, progress, status) VALUES (%s, %s, %s, %s)"
        for i in range(N):
            cur.execute(
                sql,
                (ids["user"][i], ids["task"][i], "{}", 0),
            )
        print("  ly_user_task: 15")

        # 24. ly_course_comment
        sql = (
            "INSERT INTO ly_course_comment (course_id, chapter_id, user_id, parent_id, content, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        for i in range(N):
            cur.execute(
                sql,
                (
                    ids["course"][i],
                    ids["chapter"][i],
                    ids["user"][i],
                    None,
                    f"演示评论内容{i}",
                    1,
                ),
            )
        print("  ly_course_comment: 15")

        # 25. ly_knowledge
        sql = (
            "INSERT INTO ly_knowledge (title, category, file_name, file_url, file_size, file_type, sort, visibility) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        ids["knowledge"] = []
        for i in range(1, N + 1):
            lid = insert_one(
                cur,
                sql,
                (
                    f"演示知识{i}",
                    "制度文档",
                    f"doc_{i}.pdf",
                    f"/knowledge/demo_{i}.pdf",
                    5000 * i,
                    "pdf",
                    i,
                    1,
                ),
            )
            ids["knowledge"].append(lid)
        print("  ly_knowledge: 15")

        # 26. ly_knowledge_department
        sql = "INSERT INTO ly_knowledge_department (knowledge_id, department_id) VALUES (%s, %s)"
        for i in range(N):
            cur.execute(sql, (ids["knowledge"][i], ids["department"][i]))
        print("  ly_knowledge_department: 15")

        # 27. ly_point_log
        sql = "INSERT INTO ly_point_log (user_id, points, rule_key, ref_type, ref_id, remark) VALUES (%s, %s, %s, %s, %s, %s)"
        for i in range(N):
            cur.execute(
                sql,
                (ids["user"][i], 10, f"demo_rule_{i + 1}", "course", ids["course"][i], f"演示积分{i}"),
            )
        print("  ly_point_log: 15")

        # 28. ly_image
        sql = "INSERT INTO ly_image (name, path, file_size) VALUES (%s, %s, %s)"
        for i in range(1, N + 1):
            cur.execute(sql, (f"demo_img_{i}.jpg", f"images/demo/{i}.jpg", 1024 * i))
        print("  ly_image: 15")

        # 29. ly_file_upload (file_id 唯一)
        sql = (
            "INSERT INTO ly_file_upload (file_id, file_name, file_size, file_type, chunk_size, total_chunks, uploaded_chunks, upload_path, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        file_ids = []
        for i in range(1, N + 1):
            fid = f"demo_upload_{i}_{ids['course'][0]}"
            file_ids.append(fid)
            insert_one(
                cur,
                sql,
                (fid, f"demo_{i}.mp4", 1000000 * i, "video/mp4", 5242880, 5, 5, f"/videos/demo_{i}.mp4", 1),
            )
        print("  ly_file_upload: 15")

        # 30. ly_file_chunk (file_id, chunk_index 唯一) — 15 条，每条不同 file_id、chunk_index 0
        sql = "INSERT INTO ly_file_chunk (file_id, chunk_index, chunk_size, chunk_path) VALUES (%s, %s, %s, %s)"
        for i in range(N):
            cur.execute(sql, (file_ids[i], 0, 1024000, f"/chunks/{file_ids[i]}_0.part"))
        print("  ly_file_chunk: 15")

        # 31. ly_user_course (uk user_id, course_id)
        sql = "INSERT INTO ly_user_course (user_id, course_id, progress, status) VALUES (%s, %s, %s, %s)"
        for i in range(N):
            cur.execute(sql, (ids["user"][i], ids["course"][i], min(100, 20 + i * 5), 1 if i % 3 == 0 else 0))
        print("  ly_user_course: 15")

        # 32. ly_user_video_progress (uk user_id, video_id)
        sql = "INSERT INTO ly_user_video_progress (user_id, video_id, progress, duration, is_finished) VALUES (%s, %s, %s, %s, %s)"
        for i in range(N):
            cur.execute(sql, (ids["user"][i], ids["video"][i], 60 + i * 10, 120 + i * 30, 1 if i % 2 == 0 else 0))
        print("  ly_user_video_progress: 15")

        # 33. ly_video_like（表可能不存在，Alembic v13 / Flyway V14）
        try:
            sql = "INSERT INTO ly_video_like (user_id, video_id) VALUES (%s, %s)"
            for i in range(N):
                cur.execute(sql, (ids["user"][i], ids["video"][i]))
            print("  ly_video_like: 15")
        except Exception as e:
            if "1146" in str(e) or "doesn't exist" in str(e).lower():
                print("  ly_video_like: 跳过（表不存在，请执行 Alembic v13 或 Flyway V14）")
            else:
                raise

        # 34. ly_course_video（表可能不存在，Alembic v14 / Flyway V15）
        try:
            sql = "INSERT INTO ly_course_video (course_id, video_id, chapter_id, sort) VALUES (%s, %s, %s, %s)"
            for i in range(N):
                cur.execute(sql, (ids["course"][i], ids["video"][i], ids["chapter"][i], i))
            print("  ly_course_video: 15")
        except Exception as e:
            if "1146" in str(e) or "doesn't exist" in str(e).lower():
                print("  ly_course_video: 跳过（表不存在，请执行 Alembic v14 或 Flyway V15）")
            else:
                raise

        # 35. ly_course_exam（表可能不存在，Alembic v16 / Flyway V17）
        try:
            sql = "INSERT INTO ly_course_exam (course_id, exam_id) VALUES (%s, %s)"
            for i in range(N):
                cur.execute(sql, (ids["course"][i], ids["exam"][i]))
            print("  ly_course_exam: 15")
        except Exception as e:
            if "1146" in str(e) or "doesn't exist" in str(e).lower():
                print("  ly_course_exam: 跳过（表不存在，请执行 Alembic v16 或 Flyway V17）")
            else:
                raise

        conn.commit()
        print("\n全部 demo 数据插入完成。")
    except Exception as e:
        conn.rollback()
        print(f"\n错误: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
