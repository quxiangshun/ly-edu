# -*- coding: utf-8 -*-
"""
生成各类型试题（仅 demo/示例数据）并插入数据库，用于演示与联调。
题型：single-单选，multi-多选，judge-判断，fill-填空，short-简答。
在 lyedu-api-python 目录下执行：python scripts/seed_questions.py
"""
import json
import sys
from pathlib import Path

# 保证可导入项目模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import db


def insert_question(type_: str, title: str, options=None, answer=None, score=10, analysis=None, sort=0):
    """插入一道题，options 为 JSON 字符串或 None。"""
    opts = json.dumps(options, ensure_ascii=False) if options is not None else None
    sql = (
        "INSERT INTO ly_question (type, title, options, answer, score, analysis, sort) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    return db.execute_insert(sql, (type_, title, opts, answer or "", score, analysis or "", sort))


def main():
    questions = [
        # ---------- 单选 single ----------
        {
            "type": "single",
            "title": "以下哪项是 LyEdu 平台的主要功能？",
            "options": ["A. 仅视频播放", "B. 在线学习与考试", "C. 仅文档管理", "D. 仅聊天"],
            "answer": "B",
            "score": 5,
            "analysis": "LyEdu 为企业培训平台，支持课程学习、考试、证书等完整学习流程。",
            "sort": 10,
        },
        {
            "type": "single",
            "title": "考试及格分数默认是多少？",
            "options": ["A. 50 分", "B. 60 分", "C. 70 分", "D. 80 分"],
            "answer": "B",
            "score": 5,
            "analysis": "系统默认及格分为 60，可在试卷或考试中自定义。",
            "sort": 11,
        },
        {
            "type": "single",
            "title": "课程可见性为「私有」时，可见范围是？",
            "options": ["A. 所有人", "B. 仅管理员", "C. 指定部门", "D. 仅教师"],
            "answer": "C",
            "score": 5,
            "analysis": "私有课程需关联部门，仅关联部门下的学员可见。",
            "sort": 12,
        },
        # ---------- 多选 multi ----------
        {
            "type": "multi",
            "title": "以下哪些属于 LyEdu 的典型功能？（多选）",
            "options": ["A. 课程与章节", "B. 试卷与考试", "C. 证书与积分", "D. 社交论坛"],
            "answer": "ABC",
            "score": 10,
            "analysis": "平台包含课程、考试、证书、积分等，暂无内置社交论坛。",
            "sort": 20,
        },
        {
            "type": "multi",
            "title": "试题题型包含以下哪几种？（多选）",
            "options": ["A. 单选题", "B. 多选题", "C. 判断题", "D. 填空题", "E. 简答题"],
            "answer": "ABCDE",
            "score": 10,
            "analysis": "系统支持单选、多选、判断、填空、简答五种题型。",
            "sort": 21,
        },
        # ---------- 判断 judge ----------
        {
            "type": "judge",
            "title": "学员完成培训任务后可以自动获得证书。",
            "options": ["正确", "错误"],
            "answer": "T",
            "score": 5,
            "analysis": "任务可配置完成后颁发证书，由管理员在任务中设置。",
            "sort": 30,
        },
        {
            "type": "judge",
            "title": "试卷一旦创建就不能再修改题目。",
            "options": ["正确", "错误"],
            "answer": "F",
            "score": 5,
            "analysis": "试卷可随时编辑，增删题目或调整分值。",
            "sort": 31,
        },
        {
            "type": "judge",
            "title": "防拖拽、禁止倍速等播放限制可在系统配置中设置。",
            "options": ["正确", "错误"],
            "answer": "T",
            "score": 5,
            "analysis": "在后台「系统设置」-「播放器设置」中可配置。",
            "sort": 32,
        },
        # ---------- 填空 fill ----------
        {
            "type": "fill",
            "title": "LyEdu 中试题表名为 ly_____。（填一个单词）",
            "options": None,
            "answer": "question",
            "score": 5,
            "analysis": "试题表名为 ly_question。",
            "sort": 40,
        },
        {
            "type": "fill",
            "title": "考试记录表中，用户得分字段名为 _____。",
            "options": None,
            "answer": "score",
            "score": 5,
            "analysis": "ly_exam_record 表中有 score 字段记录得分。",
            "sort": 41,
        },
        {
            "type": "fill",
            "title": "判断题的参考答案用字母 _____ 表示正确，_____ 表示错误。",
            "options": None,
            "answer": "T；F",
            "score": 5,
            "analysis": "T 表示正确（True），F 表示错误（False）。",
            "sort": 42,
        },
        # ---------- 简答 short ----------
        {
            "type": "short",
            "title": "请简述 LyEdu 平台中「周期任务」的典型应用场景。",
            "options": None,
            "answer": "用于新员工入职培训、定期安全考试、年度考核等需要按周期或一次性完成的学习与考核任务。",
            "score": 10,
            "analysis": "周期任务可配置闯关内容（课程/考试）、完成证书、指派部门等。",
            "sort": 50,
        },
        {
            "type": "short",
            "title": "组卷时「试卷-试题关联表」的作用是什么？",
            "options": None,
            "answer": "记录某张试卷包含哪些题目、每题分值及题目顺序，实现灵活组卷。",
            "score": 10,
            "analysis": "ly_paper_question 表关联 paper_id 与 question_id，并保存 score、sort。",
            "sort": 51,
        },
    ]

    inserted = 0
    for q in questions:
        try:
            insert_question(
                type_=q["type"],
                title=q["title"],
                options=q.get("options"),
                answer=q.get("answer"),
                score=q.get("score", 10),
                analysis=q.get("analysis"),
                sort=q.get("sort", 0),
            )
            inserted += 1
            print(f"  [{q['type']}] {q['title'][:40]}...")
        except Exception as e:
            print(f"  跳过: {q['title'][:40]}... 错误: {e}")

    print(f"\n共插入 {inserted} 道试题。")


if __name__ == "__main__":
    main()
