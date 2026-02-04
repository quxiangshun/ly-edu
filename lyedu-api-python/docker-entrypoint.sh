#!/bin/sh
set -e
# 等待 MySQL 可连接（compose 的 depends_on + healthcheck 后通常已就绪，此处做简短重试）
wait_for_mysql() {
    host="${MYSQL_HOST:-mysql}"
    port="${MYSQL_PORT:-3306}"
    user="${MYSQL_USERNAME:-root}"
    pass="${MYSQL_PASSWORD:-lyedu123456}"
    db="${MYSQL_DATABASE:-lyedu}"
    tries=0
    max=30
    while [ "$tries" -lt "$max" ]; do
        if python3 -c "
import sys
import pymysql
try:
    pymysql.connect(host='$host', port=$port, user='$user', password='$pass', database='$db', connect_timeout=3)
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
            echo "[LyEdu] MySQL is ready."
            return 0
        fi
        tries=$((tries + 1))
        echo "[LyEdu] Waiting for MySQL ($tries/$max)..."
        sleep 2
    done
    echo "[LyEdu] MySQL did not become ready in time." >&2
    return 1
}

wait_for_mysql

# 执行数据库迁移（与 Flyway 一致，按版本自动升级，用户无需关心）
echo "[LyEdu] Running database migrations (Alembic upgrade head)..."
alembic -c alembic.ini upgrade head
echo "[LyEdu] Migrations done. Starting API."

# 启动应用（不再在应用内重复执行迁移）
exec uvicorn main:app --host 0.0.0.0 --port 9700
