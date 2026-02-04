# 需在仓库根目录构建：docker build -f lyedu-api-python/Dockerfile .
# 以便包含 db/alembic 迁移脚本（国内可配置 DOCKER_REGISTRY 使用镜像）
FROM python:3.12-slim

WORKDIR /workspace

# 复制 Python 项目与统一迁移目录（与 Flyway 同源）
COPY lyedu-api-python /workspace/lyedu-api-python
COPY db /workspace/db

WORKDIR /workspace/lyedu-api-python

RUN pip install --no-cache-dir -r requirements.txt \
    && chmod +x docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 9700

ENTRYPOINT ["./docker-entrypoint.sh"]
