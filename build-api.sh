#!/bin/bash
# LyEdu API 构建脚本（Linux/Mac）
# 使用 Gradle 构建并复制 jar 到 pkg 目录

echo "========================================"
echo "LyEdu API - Gradle 构建"
echo "========================================"
echo ""

API_DIR="$(cd "$(dirname "$0")" && pwd)/lyedu-api"
PKG_DIR="$(cd "$(dirname "$0")" && pwd)/pkg"

if [ ! -d "$API_DIR" ]; then
    echo "错误: 找不到 lyedu-api 目录"
    exit 1
fi

# 确保 pkg 目录存在
mkdir -p "$PKG_DIR"

cd "$API_DIR" || exit 1

# 检查 Gradle Wrapper
if [ ! -f "./gradlew" ]; then
    echo "错误: 找不到 Gradle Wrapper"
    echo "请先运行: gradle wrapper"
    exit 1
fi

echo "开始构建..."
echo ""

# 执行构建
./gradlew bootJar

if [ $? -ne 0 ]; then
    echo "构建失败！"
    exit 1
fi

echo ""
echo "构建成功！"

# 检查 jar 是否已复制到 pkg 目录
JAR_PATH="$PKG_DIR/lyedu-api.jar"
if [ -f "$JAR_PATH" ]; then
    echo "JAR 文件位置: $JAR_PATH"
    echo "文件大小: $(du -h "$JAR_PATH" | cut -f1)"
else
    echo "警告: JAR 文件未找到在 pkg 目录"
    echo "请检查构建输出"
fi

echo ""
echo "下一步："
echo "  docker-compose build api"
echo "  docker-compose up -d"
echo ""
