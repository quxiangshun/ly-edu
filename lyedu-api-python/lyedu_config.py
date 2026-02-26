# -*- coding: utf-8 -*-
"""
LyEdu 配置模板生成及加载

配置路径：~/.lyedu/conf/
- config.ini.template：模板文件（程序自动生成，用户参考）
- config.ini：实际配置文件（用户复制模板后填写）

优先使用 config.ini；若不存在则生成 config.ini.template 并提示用户复制后修改。
"""
import configparser
import os
import sys
from typing import Optional, Tuple


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
# MySQL 密码（无密码则留空）
password = your_mysql_password_here
# 数据库名（必填）
database = lyedu
# 字符集（建议 utf8mb4）
charset = utf8mb4

[redis]
# Redis 服务器地址（必填）
host = 127.0.0.1
# Redis 端口（必填，默认 6379）
port = 6379
# Redis 数据库编号（必填，默认 0）
db = 0
# Redis 密码（无密码则留空）
password = your_redis_password_here
"""
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(template_content)
    print(f"[LyEdu] 配置模板已生成：{template_path}")


def _validate_config(config: configparser.ConfigParser) -> None:
    """校验配置项合法性"""
    if not config.has_section("mysql") or not config.has_section("redis"):
        raise ValueError("配置文件缺少 [mysql] 或 [redis] 节点")

    mysql_required = ["host", "port", "user", "database"]
    redis_required = ["host", "port", "db"]

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


def ensure_config_or_exit() -> bool:
    """
    确保有可用的配置来源：
    - 若 ~/.lyedu/conf/config.ini 存在：返回 True，调用方需从 config.ini 加载
    - 若不存在：创建目录、生成 config.ini.template，若无 .env 则退出

    返回 True 表示应使用 config.ini，False 表示应使用 .env（若存在）
    """
    config_dir, template_path, config_path = get_config_paths()

    if os.path.exists(config_path):
        return True

    # config.ini 不存在：确保目录存在
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, mode=0o700)
            print(f"[LyEdu] 配置目录已创建：{config_dir}")
        except PermissionError:
            print(f"[LyEdu] 无权限创建配置目录 {config_dir}，请以管理员身份运行")
            sys.exit(1)
        except OSError as e:
            print(f"[LyEdu] 创建配置目录失败：{e}")
            sys.exit(1)

    # 生成模板
    generate_config_template(template_path)

    # 检查项目目录是否有 .env 或 .env.dev（开发环境可继续）
    from pathlib import Path
    _config_dir = Path(__file__).resolve().parent
    has_env = (_config_dir / ".env").exists() or (_config_dir / ".env.dev").exists()

    if not has_env:
        print("\n[LyEdu] 未找到配置文件，请执行以下操作：")
        if sys.platform.startswith("win"):
            print(f'  1. 复制模板：copy "{template_path}" "{config_path}"')
        else:
            print(f"  1. 复制模板：cp {template_path} {config_path}")
        print(f"  2. 编辑配置：打开 {config_path} 填写 MySQL/Redis 信息")
        print("  3. 重新运行程序")
        sys.exit(1)

    # 有 .env，使用 .env 继续
    return False


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
    os.environ["REDIS_PORT"] = str(redis.getint("port", 6379))
    os.environ["REDIS_DB"] = str(redis.getint("db", 0))
    pw = redis.get("password", "").strip()
    os.environ["REDIS_PASSWORD"] = pw if pw else ""
