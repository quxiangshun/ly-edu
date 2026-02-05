# LyEdu Python 后端：视频与图片处理实现方案

本文档描述 lyedu-api-python 中**视频分片上传、视频播放**与**图片上传**的实现方案、面临的问题及解决方式，供后续维护与扩展参考。

---

## 一、目标与约束

| 目标 | 说明 |
|------|------|
| **资源只保留一份** | 不论视频/图片改不改名，相同内容（相同 SHA256）在磁盘上只存一份，避免重复占用 |
| **视频大文件** | 支持分片上传、断点续传、秒传，合并后按内容哈希去重 |
| **图片** | 上传时按内容哈希去重，同一张图只存一份物理文件 |
| **视频播放** | 浏览器原生播放，支持拖拽进度条、倍速等，需支持 HTTP Range |

---

## 二、技术选型与配置

- **哈希算法**：SHA256（`config.HASH_ALGORITHM`），与 Java 端一致，便于跨端秒传
- **分片大小**：默认 5MB（`config.CHUNK_SIZE`），可通过环境变量 `UPLOAD_CHUNK_SIZE` 覆盖
- **存储**：本地目录 `UPLOAD_PATH`（默认 `./uploads`），视频在 `videos/{file_id}/`，图片在 `images/by_hash/`
- **数据库**：`ly_file_hash` 表存 `(content_hash, relative_path, file_size)`，用于内容唯一性与秒传/去重

涉及文件：

- `config.py`：`CHUNK_SIZE`、`HASH_ALGORITHM`、`ALLOWED_VIDEO_EXT`、`ALLOWED_IMAGE_EXT`
- `util/upload_util.py`：`get_file_hash`、`get_chunk_hash`、`parse_range_header`

---

## 三、视频处理

### 3.1 流程概览

```
前端选文件 → 计算整体 SHA256 → 调用 /api/upload/check（秒传）
    → 若已存在：直接返回 video_url，结束
    → 若不存在：/api/upload/init → 按片上传 /api/upload/chunk（可带 chunkHash）→ /api/upload/merge
    → 合并后计算 SHA256，查 ly_file_hash 去重，返回 url
```

### 3.2 面临的问题与解决

#### 问题 1：同一视频多次上传或改名上传，导致重复存储

- **现象**：用户多次上传同一文件或改文件名上传，磁盘存多份相同内容。
- **解决**：
  - 合并完成后对**整文件**计算 SHA256，写入/查询 `ly_file_hash`。
  - 若 `ly_file_hash` 中已存在该 `content_hash`，则**删除本次合并得到的文件**，并将本次上传记录指向已有 `relative_path`（`upload_service.merge_chunks`）。
  - 这样无论文件名如何，只要内容一致就只保留一份。

#### 问题 2：大文件上传易失败，且失败后需重传整个文件

- **现象**：单次上传大视频容易超时或中断，重传成本高。
- **解决**：
  - **分片上传**：按固定大小（如 5MB）切分，每片单独上传（`/api/upload/chunk`），由后端按 `file_id` + `chunk_index` 落盘并记录到 `ly_file_chunk`。
  - **断点续传**：`/api/upload/init` 与 `/api/upload/progress/{file_id}` 返回已上传分片索引，前端只传未完成分片。
  - 所有分片就绪后调用 `/api/upload/merge/{file_id}` 在服务端按序合并为单一文件。

#### 问题 3：已存在的文件再次上传仍要走完分片流程，浪费带宽和时间

- **现象**：同一内容（如同一课程视频）被多人或多次上传，每次都完整上传。
- **解决**：
  - **秒传**：上传前前端对文件计算 SHA256，调用 **POST /api/upload/check**，传 `fileHash`、`fileExt`。
  - 后端在 `ly_file_hash` 中查 `content_hash`，若存在则直接返回 `is_exist: true` 和已有 `video_url`，前端不再发起分片上传。

#### 问题 4：分片在传输或存储过程中损坏，导致合并后视频无法播放

- **现象**：网络或磁盘异常导致某一片数据错误，合并后文件不可用。
- **解决**：
  - 分片上传接口支持可选表单项 **chunkHash**（前端对该片内容计算的 SHA256）。
  - 后端在 `upload_service.upload_chunk` 中用 `get_chunk_hash(chunk_data)` 校验，不一致则抛出 `ValueError`，路由返回 400，避免错误分片落盘。

#### 问题 5：视频播放时无法拖拽进度条或卡在开头

- **现象**：播放器需要按 Range 请求拉取片段，若服务端不支持 Range，则无法拖拽或跳转。
- **解决**：
  - 使用 **FileResponse** 提供文件（`main.py` 中 `GET /api/uploads/{path:path}`），由 Starlette/FastAPI 自动处理 **HTTP Range**。
  - 不把上传目录挂成纯静态文件，而是通过该接口返回，保证 Range 头被正确处理，从而支持拖拽、倍速等。

#### 问题 6：路径中暴露原始文件名或可预测 ID

- **现象**：URL 或路径包含用户文件名，存在隐私或可预测性问题。
- **解决**：
  - 视频使用 **file_id**（UUID 十六进制）作为目录名，文件名固定为 `video.{ext}`（`_video_storage_name`），不把原始文件名写入路径。
  - 最终访问路径形如 `/api/uploads/videos/{file_id}/video.mp4`。

### 3.3 关键代码位置

| 功能 | 位置 |
|------|------|
| 秒传校验 | `services/upload_service.py` → `file_check()`；`routers/upload.py` → POST `/check` |
| 初始化/分片/合并 | `routers/upload.py` → `/init`、`/chunk`、`/merge/{file_id}` |
| 分片校验 | `services/upload_service.py` → `upload_chunk(..., chunk_hash=...)`；`util/upload_util.py` → `get_chunk_hash()` |
| 合并与去重 | `services/upload_service.py` → `merge_chunks()`（合并后 `get_file_hash` + `ly_file_hash` 查重） |
| 视频访问与 Range | `main.py` → `GET /api/uploads/{path:path}`，`FileResponse` |

---

## 四、图片处理

### 4.1 流程概览

```
前端选择图片 → POST /api/image/upload（单文件）
    → 后端读取内容，计算 SHA256
    → 查 ly_file_hash：若已存在则复用 relative_path，不写盘、不重复插 ly_file_hash
    → 若不存在：写入 images/by_hash/{content_hash}.{ext}，并插入 ly_file_hash
    → 插入 ly_image（name, path, file_size），返回 url
```

### 4.2 面临的问题与解决

#### 问题 1：同一张图改名为多份上传，导致重复存储

- **现象**：同一张图片被命名为 a.jpg、b.png 等多次上传，磁盘多份。
- **解决**：
  - 上传时对**文件内容**计算 SHA256，以 `content_hash` 为唯一依据。
  - 新图存储路径为 `images/by_hash/{content_hash}.{ext}`，并写入 `ly_file_hash`。
  - 若 `ly_file_hash` 中已有该 `content_hash`（无论之前是图片还是视频），则**不写盘、不再次插入 ly_file_hash**，仅复用已有 `relative_path`，再插入一条 `ly_image` 记录（不同 name、同一 path），返回的 url 指向同一物理文件。

#### 问题 2：同一内容先作为视频存在，再作为图片上传

- **现象**：同一文件先被当视频上传（路径在 `videos/...`），再被当图片上传，若按“图片路径”再存一份会违背“只保留一份”。
- **解决**：
  - 图片上传时查 `ly_file_hash` 只按 `content_hash` 查，不区分类型。
  - 若已存在，则 `storage_rel = existing["relative_path"]`，可能是 `videos/xxx/video.mp4` 或 `images/by_hash/xxx.jpg`。
  - `ly_image.path` 存的是用于展示的 path（如 `by_hash/xxx.jpg` 或 `videos/xxx/video.mp4`），在 `_row_to_image` 中根据是否 `path.startswith("videos/")` 拼出 `/uploads/...` 或 `/uploads/images/...`，保证图片列表中的 url 能正确访问到**同一份**物理文件。

#### 问题 3：删除图片库某条记录时误删物理文件，影响其他引用

- **现象**：多条 `ly_image` 可能指向同一 path（by_hash 或复用视频），删一条就删文件会导致其他记录 404。
- **解决**：
  - **删除只删 ly_image 行**，不删物理文件（`image_service.delete_by_id` 仅执行 `DELETE FROM ly_image WHERE id = %s`）。
  - 物理文件与 `ly_file_hash` 由“内容唯一”策略保留，不做按引用计数的物理删除；若需回收孤立文件，可后续做定时任务按 `ly_file_hash` 与业务表联合判断再删。

### 4.3 关键代码位置

| 功能 | 位置 |
|------|------|
| 上传与内容哈希 | `services/image_service.py` → `upload()`，`get_chunk_hash(content)` |
| 复用已有路径 | `services/image_service.py` → 查 `ly_file_hash`，若存在则 `storage_rel = existing["relative_path"]` |
| path 与 url 映射 | `services/image_service.py` → `_row_to_image()`（videos/ 与 images/ 区分） |
| 删除仅删记录 | `services/image_service.py` → `delete_by_id()` |

---

## 五、公共能力与扩展

- **哈希**：`util/upload_util.py` 中 `get_file_hash(path)`、`get_chunk_hash(bytes)` 统一使用 `config.HASH_ALGORITHM`（SHA256），与 Java 端一致便于跨端秒传。
- **Range**：`parse_range_header()` 已在 `upload_util` 中实现，若将来改为自定义流式响应（如从对象存储代理）可直接使用。
- **配置**：分片大小、哈希算法、允许的扩展名均在 `config.py` 中集中配置，便于按环境调优。

---

## 六、小结

| 维度 | 视频 | 图片 |
|------|------|------|
| 唯一性 | 合并后按文件 SHA256 查 `ly_file_hash`，存在则删新文件并复用已有路径 | 上传时按内容 SHA256 查 `ly_file_hash`，存在则只加 `ly_image` 记录并复用路径 |
| 秒传/去重 | `/api/upload/check` + 合并后去重 | 上传时即时查重，不重复写盘 |
| 分片与校验 | 分片上传、可选 chunkHash 校验 | 单次上传，无需分片 |
| 播放/访问 | `/api/uploads/{path}` + FileResponse 支持 Range | 同一 url 规则，path 可能为 by_hash 或 videos/ |
| 删除 | 取消上传会删临时分片与本次记录；合并后的文件由内容唯一性保留 | 删除仅删 ly_image 行，不删物理文件 |

整体上，**视频与图片都按内容 SHA256 唯一化，改名不改内容也只保留一份**；视频支持秒传、分片、断点续传与分片校验，播放依赖现有 Range 能力；图片上传即去重，删除不碰物理文件，避免误伤共享引用。
