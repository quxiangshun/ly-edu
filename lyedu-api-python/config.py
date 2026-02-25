"""App config, mirrors Java application.yml；所有连接信息从 .env 读取"""
import os
import sys
import threading
import time
from pathlib import Path

_CONFIG_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv
    load_dotenv(_CONFIG_DIR / ".env")
    _env = os.getenv("ENV", "").strip().lower()
    if not _env:
        _choice = [None]

        def _prompt():
            try:
                _choice[0] = input("未指定 ENV，请选择环境: 1=dev, 2=prod [1/2]: ").strip() or "1"
            except (EOFError, KeyboardInterrupt):
                pass

        print("[LyEdu] 必须指定 ENV 环境（可手动执行 ENV=dev 或 ENV=prod）")
        t = threading.Thread(target=_prompt, daemon=True)
        t.start()
        for _ in range(300):
            time.sleep(1)
            if _choice[0] is not None:
                break
        if _choice[0] is None:
            print("[LyEdu] 由于长时间没有操作，已断开，需要重新执行")
            sys.exit(1)
        if _choice[0] in ("1", "dev"):
            _env = "dev"
        elif _choice[0] in ("2", "prod"):
            _env = "prod"
        else:
            _env = "dev"
        os.environ["ENV"] = _env
        print(f"[LyEdu] 已选择环境: {_env}")
    load_dotenv(_CONFIG_DIR / f".env.{_env}")
except ImportError:
    pass

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9700"))

# MySQL（主库，API 使用）
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USERNAME", os.getenv("MYSQL_USER", "root"))
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "lyedu123456")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "lyedu")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")

# Redis（若项目使用）
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "") or None
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

JWT_SECRET = os.getenv("JWT_SECRET", "lyedu_jwt_secret_key_please_change_in_production")
JWT_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE", "86400"))

# 飞书开放平台（与 Java lyedu.feishu 一致）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_REDIRECT_URI = os.getenv("FEISHU_REDIRECT_URI", "")

# 微信小程序（手机号登录、绑定 union_id）
WECHAT_MP_APP_ID = os.getenv("WECHAT_MP_APP_ID", "")
WECHAT_MP_APP_SECRET = os.getenv("WECHAT_MP_APP_SECRET", "")

# FA 同步脚本（sync_fa_to_ly.py）：数据源
FA_SOURCE_HOST = os.getenv("FA_SOURCE_HOST", "127.0.0.1")
FA_SOURCE_PORT = int(os.getenv("FA_SOURCE_PORT", "3307"))
FA_SOURCE_USER = os.getenv("FA_SOURCE_USER", "root")
FA_SOURCE_PASSWORD = os.getenv("FA_SOURCE_PASSWORD", "root")
FA_SOURCE_DATABASE = os.getenv("FA_SOURCE_DATABASE", "xjty")

# FA 同步脚本：目标库（未设置时复用 MYSQL_*）
FA_TARGET_HOST = os.getenv("FA_TARGET_HOST") or MYSQL_HOST
FA_TARGET_PORT = int(os.getenv("FA_TARGET_PORT") or str(MYSQL_PORT))
FA_TARGET_USER = os.getenv("FA_TARGET_USER") or MYSQL_USER
FA_TARGET_PASSWORD = os.getenv("FA_TARGET_PASSWORD") or MYSQL_PASSWORD
FA_TARGET_DATABASE = os.getenv("FA_TARGET_DATABASE") or MYSQL_DATABASE

# 默认使用 config 所在目录下的 uploads，确保无论从何处启动都能正确写入 lyedu-api-python/uploads
_raw = (os.getenv("UPLOAD_PATH") or "").strip()
if not _raw or _raw in ("./uploads", ".\\uploads", "uploads"):
    UPLOAD_PATH = (_CONFIG_DIR / "uploads").resolve()
else:
    p = Path(_raw)
    UPLOAD_PATH = p.resolve() if p.is_absolute() else (_CONFIG_DIR / p).resolve()
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

# 分片上传与内容去重（与豆包方案一致）
CHUNK_SIZE = int(os.getenv("UPLOAD_CHUNK_SIZE", str(5 * 1024 * 1024)))  # 5MB
HASH_ALGORITHM = "sha256"
ALLOWED_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".flv"}
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
