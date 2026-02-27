#!/usr/bin/env bash
# LyEdu API - 停止运行在指定端口的服务（默认 9700）
PORT="${PORT:-9700}"

pid=""
if command -v lsof >/dev/null 2>&1; then
    pid=$(lsof -ti:"$PORT" 2>/dev/null)
elif command -v fuser >/dev/null 2>&1; then
    # fuser 输出可能含后缀（如 12345c），取数字部分
    pid=$(fuser "$PORT"/tcp 2>/dev/null | grep -o '[0-9]*' | head -1)
fi

if [ -z "$pid" ]; then
    echo "[LyEdu] 端口 $PORT 上未发现运行中的服务"
    exit 0
fi

echo "[LyEdu] 正在停止 PID $pid (端口 $PORT) ..."
kill "$pid" 2>/dev/null || kill -9 "$pid"
echo "[LyEdu] 服务已停止"
