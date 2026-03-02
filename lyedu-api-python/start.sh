#!/usr/bin/env bash
# LyEdu API Python - 启动脚本（先执行 Alembic 迁移，再启动服务）
set -e
cd "$(dirname "$0")"

echo "Running Alembic migrations..."
alembic upgrade head || { echo "Alembic failed. Start anyway? [y/N]"; read -r r; [ "$r" = "y" ] || [ "$r" = "Y" ] || exit 1; }

echo "Starting LyEdu API (python main.py, HOST/PORT 见 .env)..."
exec python main.py
