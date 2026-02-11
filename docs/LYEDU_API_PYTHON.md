# lyedu-api-python 接口文档

本文档整理 FastAPI 服务 `lyedu-api-python` 中主要接口，说明请求方法、入参、出参结构以及功能说明，供客户端（含 uni-app x 与管理后台）对接使用。所有接口返回统一的响应结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": 1700000000
}
```

`code` 为业务状态码，`200` 表示成功；失败时 `message` 为错误描述，`data` 可能为空。除登录接口外，其余需要在请求头携带 `Authorization: Bearer <token>`。

## 认证模块 `/auth`

| 接口 | 方法 | 功能说明 |
| --- | --- | --- |
| `/auth/login` | `POST` | 账号密码登录，返回 JWT 与基础用户信息 |
| `/auth/feishu/url` | `GET` | 获取飞书授权登录地址 |
| `/auth/feishu/callback` | `POST` | 飞书登录回调，换取 JWT |

### `/auth/login`

- **请求方式**：`POST`
- **请求体**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `username` | `string` | 是 | 用户名 |
| `password` | `string` | 是 | 密码 |

- **响应 `data`**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `token` | `string` | JWT，用于后续接口鉴权 |
| `userInfo.id` | `number` | 用户 ID |
| `userInfo.username` | `string` | 用户名 |
| `userInfo.realName` | `string` | 真实姓名（可能为空） |
| `userInfo.role` | `string` | 角色：`admin` / `student` |

## 课程模块 `/course`

课程接口会自动根据用户可见性规则（公开课程、部门关联课程、标签匹配课程）过滤结果。

| 接口 | 方法 | 功能说明 |
| --- | --- | --- |
| `/course/page` | `GET` | 分页查询课程（支持标签筛选） |
| `/course/recommended` | `GET` | 获取推荐课程列表 |
| `/course/{id}` | `GET` | 获取课程详情（含章节、视频、附件） |
| `/course/{course_id}/comment` | `GET/POST` | 查询 / 新增课程评论 |
| `/course/comment/{comment_id}` | `DELETE` | 删除评论（限本人） |
| `/course/{id}/exam` | `GET/PUT` | 课程与考试关联（需管理权限） |

### `/course/page`

- **请求方式**：`GET`
- **请求参数**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `page` | `number` | 否 | 页码（默认 1） |
| `size` | `number` | 否 | 单页数量（默认 10） |
| `keyword` | `string` | 否 | 课程标题或描述关键字 |
| `categoryId` | `number` | 否 | 分类 ID |
| `tagId` | `number` | 否 | 标签 ID（与用户有效标签无关，可用于固定筛选） |

- **响应 `data.records` 中字段**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `number` | 课程 ID |
| `title` | `string` | 课程标题 |
| `cover` | `string` | 封面 URL |
| `description` | `string` | 课程描述 |
| `playCount` | `number` | 播放量（如有统计） |
| `likeCount` | `number` | 点赞数 |
| `commentCount` | `number` | 评论数 |
| `tagIds` | `number[]` | 关联标签 ID |
| `createTime` | `string` | 创建时间 |

- **分页元信息**：`total` 总记录数，`current` 当前页，`size` 每页数量，`pages` 总页数。

### `/course/{id}`

- **请求方式**：`GET`
- **路径参数**：`id` 课程 ID
- **响应 `data`**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `course` | `object` | 课程基础信息（含 `tagIds`、`department_ids` 等） |
| `videos` | `Video[]` | 视频列表 |
| `chapters` | `ChapterItem[]` | 章节与视频结构 |
| `attachments` | `CourseAttachment[]` | 附件列表 |
| `examId` | `number` | 关联考试 ID（可能为空） |
| `learnRecord` | `object` | 用户视频进度映射（登录用户） |

## 标签模块 `/tag`

| 接口 | 方法 | 功能说明 |
| --- | --- | --- |
| `/tag/list` | `GET` | 获取全部标签（管理端使用） |
| `/tag/effective` | `GET` | 获取当前用户有效标签：用户自身 + 部门 + 子部门标签；管理员返回全部标签 |
| `/tag/{id}` | `GET` | 标签详情 |
| `/tag/{id}/entities` | `PUT` | 绑定标签与用户 / 部门 / 课程 |

### `/tag/effective`

- **请求方式**：`GET`
- **响应 `data`**：`Tag[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `number` | 标签 ID |
| `name` | `string` | 标签名称 |
| `sort` | `number` | 排序值 |
| `createTime` | `string` | 创建时间 |

**业务逻辑**：

- **管理员**（`role == "admin"`）：返回全部标签。
- **普通用户**：返回有效标签，合并范围包括：
  1. 用户自身关联的标签（`ly_user_tag`）
  2. 用户所属部门关联的标签（`ly_department_tag`）
  3. 用户所属部门及其所有子部门关联的标签

该接口在学员端首页用于展示可筛选的课程标签。若无关联标签则返回空数组。

## 视频模块 `/video`

| 接口 | 方法 | 功能说明 |
| --- | --- | --- |
| `/video/page` | `GET` | 视频分页列表，可按课程、关键字、标签筛选；结合课程可见性与用户有效标签 |
| `/video/{id}` | `GET` | 获取视频详情（含播放/点赞统计、课程信息） |
| `/video/{id}/play` | `POST` | 记录播放次数 |
| `/video/{id}/like` | `POST` | 点赞视频 |
| `/video/{id}/like` | `DELETE` | 取消点赞 |
| `/video/liked` | `GET` | 获取我点赞的视频列表 |

### `/video/page`

- **请求方式**：`GET`
- **请求参数**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `page` | `number` | 否 | 页码（默认 1） |
| `size` | `number` | 否 | 每页条数（默认 10） |
| `courseId` | `number` | 否 | 按课程筛选 |
| `keyword` | `string` | 否 | 视频标题关键字 |
| `tagId` | `number` | 否 | 标签 ID。若省略且用户非管理员，则返回其“有效标签”集合内所有课程的视频；管理员会返回全部视频 |

- **请求头**：除公开课程外，需要携带 `Authorization: Bearer <token>`，以便根据用户角色、部门及标签控制可见性。

- **响应 `data.records` 中字段**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `number` | 视频 ID |
| `title` | `string` | 视频标题 |
| `cover` | `string` | 封面 URL |
| `url` | `string` | 播放地址 |
| `duration` | `number` | 时长（秒） |
| `playCount` | `number` | 播放次数 |
| `likeCount` | `number` | 点赞次数 |
| `courseId` | `number` | 所属课程 ID |
| `courseName` | `string` | 所属课程标题 |

- **分页元信息**：`total`、`current`、`size`、`pages` 同课程分页。

## 学习记录模块 `/learning`

| 接口 | 方法 | 功能说明 |
| --- | --- | --- |
| `/learning/recent` | `GET` | 最近学习课程列表 |
| `/learning/join` | `POST` | 加入课程（报名） |
| `/learning/watch` | `GET` | 获取观看历史 |

`/learning/join` 请求体示例：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `course_id` | `number` | 是 | 课程 ID |

响应成功时 `data` 为空；失败返回错误提示。

## 用户任务相关 `/user-task`

| 接口 | 方法 | 功能说明 |
| --- | --- | --- |
| `/user-task/my` | `GET` | 获取当前用户任务列表 |
| `/user-task/{taskId}` | `GET` | 获取任务详情 |
| `/user-task/{taskId}/complete` | `POST` | 完成任务 |

列表接口返回结构：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `task` | `object` | 任务信息（标题、描述） |
| `userTask` | `object` | 用户关联任务状态（`status`：0 未完成，1 已完成） |

## 响应错误示例

常见错误响应：

```json
{
  "code": 401,
  "message": "请先登录",
  "data": null,
  "timestamp": 1700001234
}
```

当 `code` 非 `200` 时需根据 `message` 提示用户或采取相应处理。

---

> 若新增接口或字段，请同步更新此文档，确保前后端一致。建议在提交 PR 前通过 `uvicorn main:app --reload` 本地验证接口行为。***
