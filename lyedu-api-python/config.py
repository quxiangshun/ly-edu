"""App config, mirrors Java application.yml；打包用 ~/.lyedu/conf/config.ini，开发用 .env"""
import os
import sys
from pathlib import Path

# 打包为 exe 时，__file__ 指向临时解压目录；UPLOAD_PATH 等使用 exe 所在目录
_CONFIG_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

if getattr(sys, "frozen", False):
    # 打包：仅 ~/.lyedu/conf/config.ini
    import lyedu_config
    if lyedu_config.ensure_config_or_exit():
        _, template_path, config_path = lyedu_config.get_config_paths()
        try:
            cfg = lyedu_config.load_config_ini(config_path)
            lyedu_config.apply_config_ini_to_environ(cfg)
            # 启动前验证 MySQL、Redis 连接，配置错误时提示并退出
            err = lyedu_config.test_mysql_connection()
            if err:
                print(f"[LyEdu] MySQL 连接失败：{err}")
                lyedu_config._pause_if_frozen(
                    f"MySQL 连接失败，请检查 config.ini 中的配置是否正确。\n\n"
                    f"常见原因：\n"
                    f"· MySQL 服务未启动\n"
                    f"· 主机/端口/用户名/密码填写错误\n"
                    f"· 数据库不存在\n\n"
                    f"错误详情：{err}"
                )
                sys.exit(1)
            err = lyedu_config.test_redis_connection()
            if err:
                print(f"[LyEdu] Redis 连接失败：{err}")
                lyedu_config._pause_if_frozen(
                    f"Redis 连接失败，请检查 config.ini 中的配置是否正确。\n\n"
                    f"常见原因：\n"
                    f"· Redis 服务未启动\n"
                    f"· 主机/端口/密码填写错误\n\n"
                    f"错误详情：{err}"
                )
                sys.exit(1)
        except Exception as e:
            err_msg = f"[LyEdu] 配置文件格式错误：{e}\n请参考模板文件 {template_path} 检查配置格式"
            print(err_msg)
            lyedu_config._pause_if_frozen(str(e))
            sys.exit(1)
else:
    # 开发：使用 .env，不使用 config.ini
    try:
        from dotenv import load_dotenv
        load_dotenv(_CONFIG_DIR / ".env")
        load_dotenv(_CONFIG_DIR / ".env.dev")
    except ImportError:
        pass
    # 开发环境也验证 MySQL、Redis 连接
    import lyedu_config
    err = lyedu_config.test_mysql_connection()
    if err:
        print(f"[LyEdu] MySQL 连接失败：{err}")
        print("[LyEdu] 请检查 .env 或 .env.dev 中的 MYSQL_* 配置")
        sys.exit(1)
    err = lyedu_config.test_redis_connection()
    if err:
        print(f"[LyEdu] Redis 连接失败：{err}")
        print("[LyEdu] 请检查 .env 或 .env.dev 中的 REDIS_* 配置")
        sys.exit(1)

# ENV：开发默认 dev；生产环境命令行启动必须添加 ENV=prod
os.environ.setdefault("ENV", "dev")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9700"))

# MySQL（主库，API 使用）
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USERNAME", os.getenv("MYSQL_USER", "root"))
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "lyedu123456")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "lyedu")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")

# Redis（若项目使用）；Redis 7 需提供默认用户名
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "default")
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
