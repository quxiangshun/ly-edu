"""App config, mirrors Java application.yml"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9700"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USERNAME", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "lyedu123456")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "lyedu")
MYSQL_CHARSET = "utf8mb4"

JWT_SECRET = os.getenv("JWT_SECRET", "lyedu_jwt_secret_key_please_change_in_production")
JWT_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE", "86400"))

# 飞书开放平台（与 Java lyedu.feishu 一致；扩展：后续可加 DINGTALK_* / WECOM_*）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_REDIRECT_URI = os.getenv("FEISHU_REDIRECT_URI", "")

UPLOAD_PATH = Path(os.getenv("UPLOAD_PATH", "./uploads"))
