# -*- coding: utf-8 -*-
"""上传与播放工具：哈希计算、Range 解析（与豆包分片上传+视频播放方案一致）"""
import hashlib
from pathlib import Path
from typing import Tuple

import config

HASH_READ_CHUNK = 1024 * 1024  # 1MB


def get_file_hash(file_path: Path) -> str:
    """计算文件整体 SHA256，用于唯一标识与去重"""
    h = hashlib.new(config.HASH_ALGORITHM)
    with open(file_path, "rb") as f:
        while True:
            data = f.read(HASH_READ_CHUNK)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def get_chunk_hash(chunk_data: bytes) -> str:
    """计算分片二进制哈希，用于分片完整性校验"""
    return hashlib.new(config.HASH_ALGORITHM, chunk_data).hexdigest()


def parse_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
    """
    解析 HTTP Range 请求头，返回 [start, end]（含 end）。
    用于视频播放按需拉取（拖拽进度条、倍速等）。
    """
    try:
        part = range_header.strip().split("=")[-1]
        start_str, end_str = part.split("-")
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
        end = min(end, file_size - 1)
        if start < 0 or start > end:
            raise ValueError("Invalid range")
        return start, end
    except Exception:
        raise ValueError("Range header parse failed")
