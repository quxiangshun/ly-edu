# -*- coding: utf-8 -*-
"""
LyEdu 配置模板生成及加载

配置路径：~/.lyedu/conf/（mac/Linux/windows 打包后统一只读此目录）
- config.ini.template：模板文件（程序自动生成，用户参考）
- config.ini：实际配置文件（用户复制模板后填写）

config.ini 不存在则生成模板并提示后退出；开发环境可选用 .env 覆盖部分变量。
"""
import configparser
import os
import sys
from typing import Optional, Tuple

from loguru import logger


def get_config_paths() -> Tuple[str, str, str]:
    """
    获取配置相关路径：
    - config_dir: 用户根目录/.lyedu/conf
    - template_path: 模板文件路径 ~/.lyedu/conf/config.ini.template
    - config_path: 实际配置文件路径 ~/.lyedu/conf/config.ini
    """
    user_home = os.path.expanduser("~")
    config_dir = os.path.join(user_home, ".lyedu", "conf")
    template_path = os.path.join(config_dir, "config.ini.template")
    config_path = os.path.join(config_dir, "config.ini")
    return config_dir, template_path, config_path


def generate_config_template(template_path: str) -> None:
    """生成配置模板文件"""
    template_content = """# LyEdu 配置模板文件
# 请将此文件复制为 config.ini 并填写实际的 MySQL/Redis 配置
# 保存路径：~/.lyedu/conf/config.ini

[mysql]
# MySQL 服务器地址（必填）
host = 127.0.0.1
# MySQL 端口（必填，默认 3306）
port = 3306
# MySQL 用户名（必填）
user = root
# MySQL 密码（与 compose-mysql-redis.yml 一致；无密码则留空）
password = Lyedu@123
# 数据库名（必填）
database = lyedu
# 字符集（建议 utf8mb4）
charset = utf8mb4

[redis]
# Redis 服务器地址（必填）
host = 127.0.0.1
# Redis 7 默认用户名（必填，通常为 default）
user = default
# Redis 端口（必填，默认 6379）
port = 6379
# Redis 数据库编号（必填，默认 0）
db = 0
# Redis 密码（与 compose-mysql-redis.yml 一致；无密码则留空）
password = Lyedu@123
"""
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(template_content)
    logger.info("配置模板已生成：{}", template_path)


def _validate_config(config: configparser.ConfigParser) -> None:
    """校验配置项合法性"""
    if not config.has_section("mysql") or not config.has_section("redis"):
        raise ValueError("配置文件缺少 [mysql] 或 [redis] 节点")

    mysql_required = ["host", "port", "user", "database"]
    redis_required = ["host", "port", "db", "user"]

    for item in mysql_required:
        value = config.get("mysql", item, fallback="").strip()
        if not value:
            raise ValueError(f"MySQL 配置项 '{item}' 不能为空")

    for item in redis_required:
        value = config.get("redis", item, fallback="").strip()
        if not value:
            raise ValueError(f"Redis 配置项 '{item}' 不能为空")

    try:
        mysql_port = config.getint("mysql", "port")
        redis_port = config.getint("redis", "port")
        if not (1 <= mysql_port <= 65535) or not (1 <= redis_port <= 65535):
            raise ValueError("端口号必须在 1-65535 之间")
    except ValueError as e:
        if "invalid literal" in str(e).lower():
            raise ValueError("MySQL/Redis 端口必须是 1-65535 之间的整数") from e
        raise


def load_config_ini(config_path: str) -> Optional[configparser.ConfigParser]:
    """
    从 config.ini 加载配置，校验通过后返回 ConfigParser，失败返回 None
    """
    config = configparser.ConfigParser()
    try:
        config.read(config_path, encoding="utf-8")
        _validate_config(config)
        return config
    except (configparser.Error, ValueError):
        raise


def _pause_if_frozen(msg: str = ""):
    """打包 exe 时退出前暂停，便于查看错误信息；Windows 用消息框，避免控制台闪退"""
    if not getattr(sys, "frozen", False):
        return
    if sys.platform.startswith("win"):
        import ctypes
        text = msg or "请完成配置后重新运行程序。"
        ctypes.windll.user32.MessageBoxW(  # type: ignore
            None,
            text,
            "LyEdu - 配置未就绪",
            0x40,  # MB_ICONINFORMATION
        )
    else:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            input("\n按回车键退出...")
        except (EOFError, KeyboardInterrupt):
            pass


def ensure_config_or_exit() -> bool:
    """
    打包后（mac/Linux/windows）仅读取 ~/.lyedu/conf/config.ini，不存在则生成模板并提示后退出。
    """
    config_dir, template_path, config_path = get_config_paths()

    if os.path.exists(config_path):
        return True

    # config.ini 不存在：创建目录、生成模板、提示并退出
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, mode=0o700)
            logger.info("配置目录已创建：{}", config_dir)
        except PermissionError:
            logger.error("无权限创建配置目录 {}，请以管理员身份运行", config_dir)
            _pause_if_frozen(f"无权限创建配置目录：{config_dir}\n请以管理员身份运行。")
            sys.exit(1)
        except OSError as e:
            logger.error("创建配置目录失败：{}", e)
            _pause_if_frozen(f"创建配置目录失败：{e}")
            sys.exit(1)

    generate_config_template(template_path)
    logger.warning("未找到配置文件，请执行以下操作：")
    if sys.platform.startswith("win"):
        copy_cmd = f'copy "{template_path}" "{config_path}"'
        logger.info("  1. 复制模板：{}", copy_cmd)
        msg = (
            "未找到配置文件 config.ini\n\n"
            "请执行以下操作：\n"
            "1. 复制模板：config.ini.template → config.ini\n"
            f"   路径：{config_dir}\n\n"
            "2. 用记事本打开 config.ini，填写 MySQL/Redis 信息\n\n"
            "3. 保存后重新运行本程序"
        )
    else:
        logger.info("  1. 复制模板：cp {} {}", template_path, config_path)
        msg = f"未找到配置文件。请复制 {template_path} 为 {config_path}，填写 MySQL/Redis 后重试。"
    logger.info("  2. 编辑配置：打开 {} 填写 MySQL/Redis 信息", config_path)
    logger.info("  3. 重新运行程序")
    _pause_if_frozen(msg)
    sys.exit(1)


def ensure_mysql_database() -> Optional[str]:
    """若数据库不存在则自动创建，成功返回 None，失败返回错误信息"""
    try:
        import pymysql
        db_name = os.environ.get("MYSQL_DATABASE", "lyedu").strip()
        if not db_name:
            return "MYSQL_DATABASE 未配置"
        if "`" in db_name or not all(c.isalnum() or c in "_-" for c in db_name):
            return "MYSQL_DATABASE 只能包含字母、数字、下划线和连字符"
        conn = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=None,  # 不指定库，以便在库不存在时也能连接
            charset=os.environ.get("MYSQL_CHARSET", "utf8mb4"),
            connect_timeout=5,
        )
        try:
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            logger.info("数据库 {} 已就绪（不存在时已自动创建）", db_name)
        finally:
            conn.close()
        return None
    except Exception as e:
        return str(e)


def test_mysql_connection() -> Optional[str]:
    """测试 MySQL 连接，成功返回 None，失败返回错误信息"""
    try:
        import pymysql
        conn = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "lyedu"),
            charset=os.environ.get("MYSQL_CHARSET", "utf8mb4"),
            connect_timeout=5,
        )
        conn.close()
        return None
    except Exception as e:
        return str(e)


def test_redis_connection() -> Optional[str]:
    """测试 Redis 连接，成功返回 None，失败返回错误信息；Redis 7 需提供默认用户名"""
    try:
        import redis
        host = os.environ.get("REDIS_HOST", "localhost").strip()
        if host == "localhost":
            host = "127.0.0.1"  # 避免 IPv6 解析导致连接失败
        pw = os.environ.get("REDIS_PASSWORD", "").strip()
        username = os.environ.get("REDIS_USERNAME", "default").strip() or "default"
        client = redis.Redis(
            host=host,
            port=int(os.environ.get("REDIS_PORT", "6379")),
            username=username,
            password=pw if pw else None,
            db=int(os.environ.get("REDIS_DB", "0")),
            decode_responses=True,
            socket_connect_timeout=10,
        )
        client.ping()
        return None
    except ImportError:
        return "未安装 redis 模块，请执行 pip install redis"
    except Exception as e:
        return str(e)


def apply_config_ini_to_environ(config: configparser.ConfigParser) -> None:
    """将 config.ini 内容写入 os.environ，供 config 模块后续读取"""
    mysql = config["mysql"]
    redis = config["redis"]
    os.environ["MYSQL_HOST"] = mysql.get("host", "localhost").strip()
    os.environ["MYSQL_PORT"] = str(mysql.getint("port", 3306))
    os.environ["MYSQL_USERNAME"] = mysql.get("user", "root").strip()
    os.environ["MYSQL_USER"] = mysql.get("user", "root").strip()
    os.environ["MYSQL_PASSWORD"] = mysql.get("password", "").strip()
    os.environ["MYSQL_DATABASE"] = mysql.get("database", "lyedu").strip()
    os.environ["MYSQL_CHARSET"] = mysql.get("charset", "utf8mb4").strip()
    os.environ["REDIS_HOST"] = redis.get("host", "localhost").strip()
    os.environ["REDIS_USERNAME"] = redis.get("user", "default").strip()
    os.environ["REDIS_PORT"] = str(redis.getint("port", 6379))
    os.environ["REDIS_DB"] = str(redis.getint("db", 0))
    pw = redis.get("password", "").strip()
    os.environ["REDIS_PASSWORD"] = pw if pw else ""
