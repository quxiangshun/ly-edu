# -*- coding: utf-8 -*-
"""LyEdu API - Python 版本 (FastAPI)"""
import os
import subprocess
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
    使用子进程执行，避免 Windows 下本进程默认 GBK 导致读取 UTF-8 迁移脚本报错。
    """
    base_dir = Path(__file__).resolve().parent
    script_dir = (base_dir.parent / "db" / "alembic").resolve()
    if not script_dir.exists():
        print("[LyEdu] [Alembic] 跳过: 未找到 db/alembic 目录（请从仓库根目录拉取代码）。", file=sys.stderr)
        return
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            r = subprocess.run(
                [sys.executable, "-m", "alembic", "-c", str(base_dir / "alembic.ini"), "upgrade", "head"],
                cwd=str(base_dir),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            if r.returncode == 0:
                if r.stdout:
                    print(r.stdout, end="", file=sys.stderr)
                print("[LyEdu] [Alembic] 数据库迁移已执行完成 (up to head)。")
                return
            err_msg = (r.stderr or r.stdout or "").strip() or f"exit code {r.returncode}"
            # 仅将明确的连接类错误视为可重试（避免 "context" 等词误判）
            is_conn = (
                "connection refused" in err_msg.lower()
                or "can't connect" in err_msg.lower()
                or "error 2003" in err_msg.lower()
                or "connection reset" in err_msg.lower()
                or "connection refused" in err_msg.lower()
            )
            if is_conn and attempt < max_attempts:
                print(f"[LyEdu] [Alembic] 第 {attempt} 次迁移失败（可能 MySQL 未就绪），{attempt} 秒后重试: {err_msg[:200]}", file=sys.stderr)
                time.sleep(attempt)
                continue
            print("[LyEdu] [Alembic] 自动迁移失败（应用仍会启动）:", err_msg[:500], file=sys.stderr)
            if r.stderr:
                print(r.stderr[:800], file=sys.stderr)
            print("[LyEdu] [Alembic] 请检查: 1) 是否已启动 MySQL（如 docker compose -f compose-mysql-redis.yml up）"
                  " 2) .env 或环境变量 MYSQL_* 是否正确（可参考 .env.example）"
                  " 3) 手动执行: cd lyedu-api-python && alembic -c alembic.ini upgrade head", file=sys.stderr)
            return
        except Exception as e:
            err_msg = str(e).strip()
            is_conn = (
                "connection refused" in err_msg.lower()
                or "can't connect" in err_msg.lower()
                or "error 2003" in err_msg.lower()
                or "connection reset" in err_msg.lower()
            )
            if is_conn and attempt < max_attempts:
                print(f"[LyEdu] [Alembic] 第 {attempt} 次迁移失败（可能 MySQL 未就绪），{attempt} 秒后重试: {e}", file=sys.stderr)
                time.sleep(attempt)
                continue
            print("[LyEdu] [Alembic] 自动迁移失败（应用仍会启动）:", e, file=sys.stderr)
            print("[LyEdu] [Alembic] 请检查: 1) 是否已启动 MySQL（如 docker compose -f compose-mysql-redis.yml up）"
                  " 2) .env 或环境变量 MYSQL_* 是否正确（可参考 .env.example）"
                  " 3) 手动执行: cd lyedu-api-python && alembic -c alembic.ini upgrade head", file=sys.stderr)
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
