# -*- coding: utf-8 -*-
"""LyEdu API - Python 版本 (FastAPI)"""
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

import config
from routers import auth, course, chapter, video, learning, user, department, stats, knowledge, question, paper, exam, exam_record, certificate_template, certificate, user_certificate, task, user_task, config as config_router, point, point_rule, image, upload


def _run_alembic_upgrade() -> None:
    """启动时自动执行 Alembic 迁移（alembic upgrade head），与 Java 端 Flyway 行为一致。
    使用 Alembic API 在进程内执行，避免子进程 python -m alembic 在某些环境（如 Python 3.14）失败。
    若数据库中曾记录为已移除的版本，会自动将 alembic_version 改为当前 head（v15）后重试。
    """
    base_dir = Path(__file__).resolve().parent
    script_dir = (base_dir.parent / "db" / "alembic").resolve()
    if not script_dir.exists():
        print("[LyEdu] [Alembic] 跳过: 未找到 db/alembic 目录（请从仓库根目录拉取代码）。", file=sys.stderr)
        return
    ini_path = base_dir / "alembic.ini"
    max_attempts = 3
    fixed_stale_revision = False
    for attempt in range(1, max_attempts + 1):
        try:
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config(str(ini_path))
            command.upgrade(alembic_cfg, "head")
            print("[LyEdu] [Alembic] 数据库迁移已执行完成 (up to head)。")
            return
        except Exception as e:
            err_msg = str(e).strip()
            # 数据库中记录为已移除的版本时，自动改为当前 head（v15）后重试一次
            if "can't locate revision identified by" in err_msg.lower() and not fixed_stale_revision:
                try:
                    import db
                    n = db.execute("UPDATE alembic_version SET version_num = %s", ("v15",))
                    if n == 0:
                        db.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", ("v15",))
                    print("[LyEdu] [Alembic] 已将数据库版本从已移除的修订改为 v15，正在重试迁移。", file=sys.stderr)
                    fixed_stale_revision = True
                    continue
                except Exception as fix_e:
                    print("[LyEdu] [Alembic] 自动修正版本失败:", str(fix_e)[:200], file=sys.stderr)
            is_conn = (
                "connection refused" in err_msg.lower()
                or "can't connect" in err_msg.lower()
                or "error 2003" in err_msg.lower()
                or "connection reset" in err_msg.lower()
            )
            if is_conn and attempt < max_attempts:
                print(f"[LyEdu] [Alembic] 第 {attempt} 次迁移失败（可能 MySQL 未就绪），{attempt} 秒后重试: {err_msg[:200]}", file=sys.stderr)
                time.sleep(attempt)
                continue
            print("[LyEdu] [Alembic] 自动迁移失败（应用仍会启动）:", err_msg[:500], file=sys.stderr)
            print("[LyEdu] [Alembic] 请检查: 1) 是否已启动 MySQL（如 docker compose -f compose-mysql-redis.yml up）"
                  " 2) .env 或环境变量 MYSQL_* 是否正确（可参考 .env.example）", file=sys.stderr)
            return


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_alembic_upgrade()
    yield


app = FastAPI(title='LyEdu API', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

# 与前端 baseURL: '/api' 一致，所有接口挂到 /api 下
API_PREFIX = '/api'

# 上传文件访问：使用 FileResponse 支持 Range 分片加载（视频拖拽、分段请求）
Path(config.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
UPLOAD_PATH_RESOLVED = config.UPLOAD_PATH.resolve()


@app.get(API_PREFIX + "/uploads/{path:path}")
def serve_upload(path: str):
    """提供上传文件，支持 HTTP Range 分片加载（视频播放器按需拉取）"""
    full = (UPLOAD_PATH_RESOLVED / path).resolve()
    if not str(full).startswith(str(UPLOAD_PATH_RESOLVED)) or ".." in path or not full.is_file():
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("Not Found", status_code=404)
    return FileResponse(str(full), media_type=None)

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(course.router, prefix=API_PREFIX)
app.include_router(chapter.router, prefix=API_PREFIX)
app.include_router(video.router, prefix=API_PREFIX)
app.include_router(learning.router, prefix=API_PREFIX)
app.include_router(user.router, prefix=API_PREFIX)
app.include_router(department.router, prefix=API_PREFIX)
app.include_router(stats.router, prefix=API_PREFIX)
app.include_router(knowledge.router, prefix=API_PREFIX)
app.include_router(question.router, prefix=API_PREFIX)
app.include_router(paper.router, prefix=API_PREFIX)
app.include_router(exam.router, prefix=API_PREFIX)
app.include_router(exam_record.router, prefix=API_PREFIX)
app.include_router(certificate_template.router, prefix=API_PREFIX)
app.include_router(certificate.router, prefix=API_PREFIX)
app.include_router(user_certificate.router, prefix=API_PREFIX)
app.include_router(task.router, prefix=API_PREFIX)
app.include_router(user_task.router, prefix=API_PREFIX)
app.include_router(config_router.router, prefix=API_PREFIX)
app.include_router(point.router, prefix=API_PREFIX)
app.include_router(point_rule.router, prefix=API_PREFIX)
app.include_router(image.router, prefix=API_PREFIX)
app.include_router(upload.router, prefix=API_PREFIX)


@app.get('/')
def root():
    return {'message': 'LyEdu API (Python)', 'docs': '/docs', 'api': API_PREFIX}


@app.get(API_PREFIX)
def api_root():
    return {'message': 'LyEdu API', 'docs': '/docs'}
