# LyEdu Python 后端：使用 Redis 做数据缓存

本文档描述**接口耗时长、超时（如 /exam/page）** 的成因、以及通过 **批量查询 + Redis 缓存** 的解决方案，并给出一步步实现方式，供遇到类似问题的人按步骤落地。

---

## 一、问题现象

| 现象 | 说明 |
|------|------|
| **接口超时** | 前端请求 `/api/exam/page?page=1&size=200` 等接口时出现 `AxiosError: timeout of 30000ms exceeded` |
| **接口变慢** | 列表/下拉数据量稍大（如 size=200）时，响应时间明显变长（数秒甚至几十秒） |
| **数据库压力大** | 同一请求触发大量 SQL，数据库连接与 QPS 偏高 |

---

## 二、问题原因（N+1 查询）

以**考试列表需要展示试卷名称**为例：

- 列表接口先查 `ly_exam` 得到 N 条考试记录（每条含 `paper_id`）。
- **原实现**：在循环里对每条考试调用 `paper_service.get_by_id(paper_id)` 查试卷名称。
- 结果：每页 N 条就产生 **1（查考试）+ N（查试卷）= N+1 次**数据库查询；size=200 时就是 201 次查询，耗时长且易超时。

```text
原逻辑（伪代码）：
  rows = SELECT * FROM ly_exam LIMIT 200
  for row in rows:
    paper = get_by_id(row.paper_id)   # 每条一次 SQL
    row.paperTitle = paper.title
```

这就是典型的 **N+1 查询**：1 次主查询 + N 次关联查询。

---

## 三、解决方案概览

从两方面同时优化：

1. **批量查询**：把「按 id 逐条查」改成「按 id 列表一次查」，例如 `get_titles_by_ids(paper_ids)` 一次 SQL 查出当前页所有试卷的 id→title，消除 N 次查询。
2. **Redis 缓存**：对读多写少的数据（如试卷名称）做缓存；先查缓存，未命中再查库并回填缓存；写操作（更新/删除）时删除对应缓存，保证一致性。

效果：

- **批量查询**：每页无论 20 还是 200 条，试卷名称只查 **1 次** 数据库。
- **Redis 缓存**：同一试卷名称被多次请求时，命中缓存不再打数据库；Redis 不可用时自动降级为只查库，不抛错。

---

## 四、一步步实现

### 4.1 添加 Redis 依赖

在 `lyedu-api-python/requirements.txt` 中增加：

```text
redis>=5.0.0
```

安装：

```bash
cd lyedu-api-python
pip install -r requirements.txt
```

---

### 4.2 确认 Redis 配置

项目已从环境变量读取 Redis 配置，无需改业务逻辑，只需保证环境正确。

**配置文件** `config.py` 中已有：

```python
# Redis（若项目使用）
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "") or None
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
```

**环境变量**（`.env` 或 `.env.dev`）示例：

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

本地开发可先不启 Redis，缓存会静默降级为不生效，接口仍正常查库。

---

### 4.3 实现 Redis 缓存工具模块

在 `util/redis_cache.py` 中实现通用缓存：get/set/delete，支持 TTL 和 JSON；Redis 不可用时静默降级（返回 None/不写缓存），不抛错。

**完整代码**（可直接作为 `lyedu-api-python/util/redis_cache.py` 使用）：

```python
# -*- coding: utf-8 -*-
"""Redis 缓存工具：get/set/delete，支持 TTL 与 JSON；Redis 不可用时静默降级，不抛错"""
import json
from typing import Any, Optional

try:
    import redis
except ImportError:
    redis = None

import config

# 全局客户端，懒加载
_client: Optional[Any] = None
_key_prefix = "lyedu:"


def _get_client():
    global _client
    if _client is not None:
        return _client
    if redis is None:
        return None
    try:
        _client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD,
            db=config.REDIS_DB,
            decode_responses=True,
        )
        _client.ping()
        return _client
    except Exception:
        _client = None
        return None


def _key(k: str) -> str:
    return _key_prefix + k if _key_prefix else k


def get(key: str) -> Optional[str]:
    """获取字符串缓存，不存在或 Redis 不可用时返回 None"""
    c = _get_client()
    if not c:
        return None
    try:
        v = c.get(_key(key))
        return v if v is None else str(v)
    except Exception:
        return None


def set(key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
    """设置字符串缓存；ttl_seconds 为 None 表示不过期。成功返回 True，失败返回 False"""
    c = _get_client()
    if not c:
        return False
    try:
        k = _key(key)
        if ttl_seconds is not None:
            c.setex(k, ttl_seconds, value)
        else:
            c.set(k, value)
        return True
    except Exception:
        return False


def delete(key: str) -> bool:
    """删除缓存。成功返回 True，失败或 Redis 不可用返回 False"""
    c = _get_client()
    if not c:
        return False
    try:
        c.delete(_key(key))
        return True
    except Exception:
        return False


def get_json(key: str) -> Optional[Any]:
    """获取 JSON 缓存（dict/list 等），不存在或解析失败或 Redis 不可用时返回 None"""
    raw = get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def set_json(key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
    """设置 JSON 缓存。成功返回 True，失败返回 False"""
    try:
        raw = json.dumps(value, ensure_ascii=False)
        return set(key, raw, ttl_seconds)
    except (TypeError, ValueError):
        return False


def is_available() -> bool:
    """当前 Redis 是否可用（用于运维或开关逻辑）"""
    return _get_client() is not None
```

**使用示例**：

```python
from util import redis_cache

# 字符串，带 5 分钟过期
redis_cache.set("user:name:1", "张三", ttl_seconds=300)
name = redis_cache.get("user:name:1")

# JSON（dict/list）
redis_cache.set_json("config:site", {"title": "学堂"}, ttl_seconds=3600)
obj = redis_cache.get_json("config:site")

# 删除
redis_cache.delete("user:name:1")
```

---

### 4.4 试卷服务：批量查询 + 缓存

试卷名称是「读多写少」的典型场景，适合：**先批量查 DB 消除 N+1，再用 Redis 按 id 缓存名称，写时删缓存**。

#### 4.4.1 在 paper_service 中增加批量接口（若无则已有）

在 `services/exam/paper_service.py` 中增加批量查「id→title」的方法（若已有 `get_titles_by_ids` 可跳过本段，仅看缓存部分）：

```python
def get_titles_by_ids(paper_ids: List[int]) -> Dict[int, Optional[str]]:
    """批量查询试卷 id -> title；先读 Redis 缓存，未命中再查库并回填缓存"""
    if not paper_ids:
        return {}
    ids = list(dict.fromkeys(paper_ids))
    result: Dict[int, Optional[str]] = {}
    miss_ids: List[int] = []
    for pid in ids:
        cached = redis_cache.get("paper:title:%s" % pid)
        if cached is not None:
            result[pid] = cached if cached else None
        else:
            miss_ids.append(pid)
    if not miss_ids:
        return result
    try:
        placeholders = ", ".join(["%s"] * len(miss_ids))
        sql = "SELECT id, title FROM ly_paper WHERE id IN (" + placeholders + ") AND deleted = 0"
        rows = db.query_all(sql, tuple(miss_ids))
        for r in (rows or []):
            pid = r["id"]
            title = r.get("title")
            result[pid] = title
            redis_cache.set("paper:title:%s" % pid, title or "", PAPER_TITLE_CACHE_TTL)
        for pid in miss_ids:
            if pid not in result:
                result[pid] = None
                redis_cache.set("paper:title:%s" % pid, "", PAPER_TITLE_CACHE_TTL)
        return result
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            for pid in miss_ids:
                result[pid] = None
            return result
        raise
```

要点：

- **缓存 key**：`paper:title:{id}`，工具层会自动加前缀 `lyedu:`。
- **TTL**：例如 `PAPER_TITLE_CACHE_TTL = 300`（5 分钟），在文件顶部定义。
- **空值也缓存**：不存在的试卷也写入空字符串，避免缓存穿透（反复查不存在的 id）。

#### 4.4.2 写操作时删除缓存

在**更新**、**删除**试卷时删除对应 key，保证后续读到的名称与数据库一致。

在 `update` 中，执行完更新后：

```python
if n > 0:
    redis_cache.delete("paper:title:%s" % paper_id)
```

在 `delete`（软删或硬删）中，执行完删除后：

```python
if n > 0:
    redis_cache.delete("paper:title:%s" % paper_id)
```

#### 4.4.3 考试列表使用批量接口

在 `services/exam/exam_service.py` 的 `page()` 中，不再循环调用 `get_by_id(pid)`，改为一次批量查并写 `paperTitle`：

```python
# 批量查试卷名称，避免 N+1
paper_ids = [r.get("paper_id") for r in (rows or []) if r.get("paper_id")]
paper_titles = paper_service.get_titles_by_ids(paper_ids) if paper_ids else {}
records = []
for r in (rows or []):
    e = _row_to_exam(r)
    pid = e.get("paperId")
    e["paperTitle"] = paper_titles.get(pid) if pid else None
    # ... 其余部门、课程等
```

这样每页只产生 **1 次** 试卷相关 DB 查询（且命中缓存时 0 次）。

---

## 五、实施检查清单

按顺序核对即可快速落地：

| 步骤 | 内容 | 说明 |
|------|------|------|
| 1 | `requirements.txt` 增加 `redis>=5.0.0` | 并执行 `pip install -r requirements.txt` |
| 2 | 确认 `config.py` 中已有 `REDIS_*` 配置 | 一般已存在，无需改代码 |
| 3 | 新增/确认 `util/redis_cache.py` | 提供 get/set/delete 与 get_json/set_json，静默降级 |
| 4 | 在 paper_service 中实现/接入 `get_titles_by_ids` | 先读缓存，未命中再查 DB 并回填；空值也缓存防穿透 |
| 5 | 在 paper 的 update/delete 中删除 `paper:title:{id}` | 保证读写一致 |
| 6 | exam_service.page() 使用 get_titles_by_ids 替代循环 get_by_id | 消除 N+1 |
| 7 | （可选）配置 .env 中 REDIS_HOST/PORT 等 | 不配置则缓存不生效，接口仍正常 |

---

## 六、扩展到其他数据（如部门名、课程名）

遇到类似「列表里要展示关联名称」的慢接口，可按同一思路处理：

1. **先消除 N+1**：抽出「按 id 列表一次查」的接口（如 `get_titles_by_ids`），在列表逻辑里一次调用，避免在循环里单条查。
2. **再按需加缓存**：
   - 在「按 id 列表查」的实现里：先按 key（如 `dept:name:{id}`）从 `redis_cache.get` 取，未命中的 id 列表再查 DB，结果写回缓存并设置 TTL。
   - 在对应实体的更新/删除处：`redis_cache.delete("dept:name:%s" % id)`。

Key 命名建议：`{业务}:{字段}:{id}`，例如 `course:title:1`、`dept:name:2`。TTL 根据变更频率定，读多写少可 300～3600 秒。

---

## 七、常见问题

**Q：不装 Redis 或 Redis 挂了会报错吗？**  
A：不会。`util/redis_cache.py` 在连接失败或未安装 `redis` 时，`get` 返回 None，`set`/`delete` 静默失败，业务只走数据库，接口正常。

**Q：如何确认缓存生效？**  
A：可先看接口耗时是否明显下降；或在代码里临时打印/打日志：命中缓存时少一次 DB 查询；也可用 Redis CLI 查看 key（如 `lyedu:paper:title:1`）。

**Q：缓存和数据库不一致怎么办？**  
A：所有**写**该数据的地方（增删改）都要在成功后执行对应的 `redis_cache.delete(key)`，保证下次读取时从 DB 拉新数据并回填缓存。

**Q：TTL 设多少合适？**  
A：读多写少、变更不频繁的（如试卷名称）可 300～600 秒；配置类可更长或不过期（ttl_seconds=None），并在后台修改配置时主动 delete 对应 key。

---

## 八、相关文件一览

| 文件 | 作用 |
|------|------|
| `config.py` | REDIS_HOST / REDIS_PORT / REDIS_PASSWORD / REDIS_DB |
| `util/redis_cache.py` | 通用 Redis 缓存 get/set/delete、get_json/set_json，静默降级 |
| `services/exam/paper_service.py` | get_titles_by_ids 批量+缓存；update/delete 删缓存 |
| `services/exam/exam_service.py` | page() 中调用 get_titles_by_ids，避免 N+1 |
| `requirements.txt` | 增加 redis>=5.0.0 |

按本文「一步步实现」和「实施检查清单」操作，即可在项目中稳定使用 Redis 做数据缓存，并解决因 N+1 导致的接口超时与变慢问题。
