# 需在仓库根目录构建：docker build -f lyedu-api-python/Dockerfile .
# 国内可配置 DOCKER_REGISTRY 使用镜像
FROM python:3.12-slim

WORKDIR /workspace

COPY lyedu-api-python /workspace/lyedu-api-python

WORKDIR /workspace/lyedu-api-python

RUN pip install --no-cache-dir -r requirements.txt \
    && chmod +x docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 9700

ENTRYPOINT ["./docker-entrypoint.sh"]
