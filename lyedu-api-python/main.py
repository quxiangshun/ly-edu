# -*- coding: utf-8 -*-
"""LyEdu API - Python 版本 (FastAPI)"""
import os
import shutil
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

# 最早初始化 loguru，供 config 等模块使用
import util.logger  # noqa: F401

from loguru import logger

# 打包 exe 时，未捕获异常退出前暂停，便于查看错误；Windows 用消息框
if getattr(sys, "frozen", False):
    _orig_excepthook = sys.excepthook
    def _excepthook(typ, val, tb):
        import traceback
        _orig_excepthook(typ, val, tb)
        err = f"{typ.__name__}: {val}" if val else str(typ)
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.user32.MessageBoxW(  # type: ignore
                None,
                f"程序异常退出：\n\n{err}\n\n详细信息见控制台输出。",
                "LyEdu - 错误",
                0x10,  # MB_ICONERROR
            )
        else:
            try:
                input("\n按回车键退出...")
            except (EOFError, KeyboardInterrupt):
                pass
        sys.exit(1)
    sys.excepthook = _excepthook

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, Response

import config
from routers import auth, course, course_attachment, chapter, video, learning, user, department, stats, knowledge, question, paper, exam, exam_status, exam_record, certificate_template, certificate, user_certificate, task, user_task, config as config_router, point, point_rule, image, upload, course_comment, tag, feishu


def _ensure_alembic_in_lyedu() -> tuple[Path, Path] | None:
    """打包 exe 时，在 ~/.lyedu 下同步 alembic 目录和 alembic.ini。
    每次启动都从 _MEIPASS 覆盖更新，确保 v1、v2、v3 等新迁移随 exe 版本同步。"""
    if not getattr(sys, "frozen", False):
        return None
    lyedu_dir = Path.home() / ".lyedu"
    alembic_dest = lyedu_dir / "alembic"
    ini_dest = lyedu_dir / "alembic.ini"
    meipass = Path(sys._MEIPASS)
    src_alembic = meipass / "alembic"
    src_ini = meipass / "alembic.ini"
    if not src_alembic.exists() or not src_ini.exists():
        return None
    lyedu_dir.mkdir(parents=True, exist_ok=True)
    # 每次启动覆盖，确保 exe 更新后 v2、v3 等新迁移能同步到 ~/.lyedu
    if alembic_dest.exists():
        shutil.rmtree(alembic_dest)
    shutil.copytree(src_alembic, alembic_dest)
    shutil.copy2(src_ini, ini_dest)
    return (ini_dest, alembic_dest)


def _run_alembic_upgrade() -> None:
    """启动时自动执行 Alembic 迁移（alembic upgrade head），与 Java 端 Flyway 行为一致。
    使用 Alembic API 在进程内执行，避免子进程 python -m alembic 在某些环境（如 Python 3.14）失败。
    若数据库中曾记录为已移除的版本（如原 v2～v16），会自动将 alembic_version 改为当前 head（v1）后重试。
    打包 exe 时使用 ~/.lyedu/alembic，与 config.ini 同一目录层级，方便用户管理。
    """
    if getattr(sys, "frozen", False):
        res = _ensure_alembic_in_lyedu()
        if res:
            ini_path, script_dir = res
        else:
            logger.warning("[Alembic] 跳过: 未找到 alembic 资源")
            return
    else:
        base_dir = Path(__file__).resolve().parent
        script_dir = (base_dir / "alembic").resolve()
        ini_path = base_dir / "alembic.ini"
        if not script_dir.exists():
            logger.warning("[Alembic] 跳过: 未找到 alembic 目录")
            return
    max_attempts = 3
    fixed_stale_revision = False
    for attempt in range(1, max_attempts + 1):
        try:
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config(str(ini_path))
            alembic_cfg.set_main_option("script_location", str(script_dir))
            command.upgrade(alembic_cfg, "head")
            logger.info("[Alembic] 数据库迁移已执行完成 (up to head)")
            return
        except Exception as e:
            err_msg = str(e).strip()
            # 数据库中记录为已移除的版本时，自动改为当前 head（v1）后重试一次
            if "can't locate revision identified by" in err_msg.lower() and not fixed_stale_revision:
                try:
                    import db
                    n = db.execute("UPDATE alembic_version SET version_num = %s", ("v1",))
                    if n == 0:
                        db.execute("INSERT INTO alembic_version (version_num) VALUES (%s)", ("v1",))
                    logger.warning("[Alembic] 已将数据库版本从已移除的修订改为 v1，正在重试迁移")
                    fixed_stale_revision = True
                    continue
                except Exception as fix_e:
                    logger.error("[Alembic] 自动修正版本失败: {}", str(fix_e)[:200])
            is_conn = (
                "connection refused" in err_msg.lower()
                or "can't connect" in err_msg.lower()
                or "error 2003" in err_msg.lower()
                or "connection reset" in err_msg.lower()
            )
            if is_conn and attempt < max_attempts:
                logger.warning("[Alembic] 第 {} 次迁移失败（可能 MySQL 未就绪），{} 秒后重试: {}", attempt, attempt, err_msg[:200])
                time.sleep(attempt)
                continue
            logger.error("[Alembic] 自动迁移失败（应用仍会启动）: {}", err_msg[:500])
            logger.error("[Alembic] 请检查: 1) 是否已启动 MySQL（如 docker compose -f compose-mysql-redis.yml up）2) ~/.lyedu/conf/config.ini 中 MYSQL_* 配置是否正确")
            return


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_alembic_upgrade()
    yield


app = FastAPI(
    title='LyEdu API',
    version='1.0.0',
    description='接口说明见 /docs（Swagger）与 docs/LYEDU_API_PYTHON.md',
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


class NoCacheMiddleware(BaseHTTPMiddleware):
    """禁止 API 响应被缓存，避免返回 304 导致客户端解析 HTML 报错"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith(API_PREFIX) and not request.url.path.startswith(API_PREFIX + "/uploads/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app.add_middleware(NoCacheMiddleware)

# 与前端 baseURL: '/api' 一致，所有接口挂到 /api 下
API_PREFIX = '/api'

# 上传文件访问：使用 FileResponse 支持 Range 分片加载（视频拖拽、分段请求）
Path(config.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
UPLOAD_PATH_RESOLVED = config.UPLOAD_PATH.resolve()
logger.info("UPLOAD_PATH = {}", UPLOAD_PATH_RESOLVED)


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
app.include_router(course_attachment.router, prefix=API_PREFIX)
app.include_router(course_comment.router, prefix=API_PREFIX)
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
app.include_router(exam_status.router, prefix=API_PREFIX)
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
app.include_router(tag.router, prefix=API_PREFIX)
app.include_router(feishu.router, prefix=API_PREFIX)


@app.get('/')
def root():
    return {
        'message': 'LyEdu API (Python)',
        'docs': '/docs',
        'api': API_PREFIX,
        'interface_doc': '/interface-doc',
        'openapi': '/openapi.json',
    }


@app.get(API_PREFIX)
def api_root():
    return {'message': 'LyEdu API', 'docs': '/docs', 'interface_doc': '/interface-doc'}


@app.get('/interface-doc', include_in_schema=False)
def serve_interface_doc():
    """提供接口说明 Markdown（仓库含 docs 时可用，Docker/打包环境可能 404）"""
    doc_path = Path(__file__).resolve().parent.parent / 'docs' / 'LYEDU_API_PYTHON.md'
    if doc_path.exists():
        return Response(content=doc_path.read_text(encoding='utf-8'), media_type='text/markdown; charset=utf-8')
    return JSONResponse({'message': 'Interface doc not found (run from repo root)'}, status_code=404)


if __name__ == "__main__":
    # 直接启动 uvicorn，HOST/PORT 从配置文件读取（.env / .env.dev，默认 0.0.0.0 / 9700）
    import uvicorn
    _reload = os.getenv("ENV", "dev") == "dev"
    try:
        if _reload:
            uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
        else:
            uvicorn.run(app, host=config.HOST, port=config.PORT)
    except Exception as e:
        err = str(e)
        logger.error("启动失败: {}", err)
        if getattr(sys, "frozen", False) and sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.user32.MessageBoxW(  # type: ignore
                None,
                f"LyEdu 服务启动失败：\n\n{err}\n\n请检查 MySQL/Redis 是否已启动、配置是否正确。",
                "LyEdu - 启动失败",
                0x10,  # MB_ICONERROR
            )
        elif getattr(sys, "frozen", False):
            try:
                input("\n按回车键退出...")
            except (EOFError, KeyboardInterrupt):
                pass
        raise
