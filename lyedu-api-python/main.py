# -*- coding: utf-8 -*-
"""LyEdu API - Python 版本 (FastAPI)"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from routers import auth, course, chapter, video, learning, user, department, stats, knowledge, question, paper, exam, exam_record, certificate_template, certificate, user_certificate, task, user_task


def _run_alembic_upgrade() -> None:
    """启动时自动执行 Alembic 迁移（alembic upgrade head）"""
    try:
        from alembic import command
        from alembic.config import Config

        # 使用与 alembic.ini 一致的 script_location（../db/alembic），需在 lyedu-api-python 目录下解析
        base_dir = Path(__file__).resolve().parent
        alembic_cfg = Config(str(base_dir / "alembic.ini"))
        # 使用绝对路径，避免 cwd 影响
        script_dir = (base_dir.parent / "db" / "alembic").resolve()
        if script_dir.exists():
            alembic_cfg.set_main_option("script_location", str(script_dir))
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        # 迁移失败不阻塞启动（如数据库未就绪），仅打日志
        import logging
        logging.getLogger(__name__).warning("Alembic upgrade on startup skipped or failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_alembic_upgrade()
    yield


app = FastAPI(title='LyEdu API', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

# 与前端 baseURL: '/api' 一致，所有接口挂到 /api 下
API_PREFIX = '/api'
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


@app.get('/')
def root():
    return {'message': 'LyEdu API (Python)', 'docs': '/docs', 'api': API_PREFIX}


@app.get(API_PREFIX)
def api_root():
    return {'message': 'LyEdu API', 'docs': '/docs'}
