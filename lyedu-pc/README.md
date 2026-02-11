# lyedu-pc

学员端 PC 前端，面向普通学员使用。管理后台为 **lyedu-admin**，后端 API 为 **lyedu-api-python**。

## 技术栈

- **Vue 3** + **TypeScript** + **Vite**
- **Element Plus**（UI 组件）
- **Vue Router**（路由）
- **Axios**（请求，封装于 `src/utils/request.ts`）
- **Pinia**（状态，当前主要用于扩展）

## 环境要求

- Node.js 18+
- npm 或 pnpm

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务

```bash
npm run dev
```

默认访问：<http://localhost:9800>。开发时请求会通过 Vite 代理到后端（默认 `http://localhost:9700`），需保证 lyedu-api-python 已启动。

### 环境变量

复制 `.env.example` 为 `.env` 并按需修改：

| 变量 | 说明 | 示例 |
|------|------|------|
| `VITE_AUTH_PROVIDER` | 登录方式 | `local`（仅账号密码）、`feishu`（仅飞书）、`both`（飞书 + 账号密码） |
| `VITE_PPTIST_URL` | PPT 制作 iframe 地址（可选） | 不设置时使用相对路径 `/pptist/`，需将 PPTist 构建产物放到 `public/pptist/` |

## 构建与部署

### 本地构建

```bash
npm run build
```

产物在 `dist/` 目录。

### Docker 部署

项目根目录提供 `Dockerfile`，多阶段构建：先构建前端，再使用 nginx 提供静态资源。

```bash
docker build -t lyedu-pc .
docker run -p 80:80 lyedu-pc
```

容器内 nginx 将 `/api`、`/uploads` 反向代理到后端服务（默认 `http://api:9700`），生产环境需通过编排或环境配置指定后端地址。

### Nginx 配置说明

- `location /`：SPA 回退到 `index.html`
- `location /api`：代理到后端 API
- `location /uploads`：代理到后端静态资源（上传文件）

### PPT 制作（PPTist 集成）

PC 端通过 **iframe** 集成 [PPTist](https://github.com/pipipi-pikachu/PPTist)（在线 PPT 编辑/演示）。入口：顶栏「学习与考试」→「PPT 制作」，路由 `/ppt`。

**使用前需自行构建并部署 PPTist 静态资源：**

1. 克隆 PPTist 仓库并构建：
   ```bash
   git clone https://github.com/pipipi-pikachu/PPTist.git
   cd PPTist
   npm install
   ```
2. 在 PPTist 的 `vite.config.ts` 中设置 `base: '/pptist/'`（便于放入 lyedu-pc 同域子路径）。
3. 构建：`npm run build`。
4. 将 PPTist 的 `dist/` 目录下**所有文件**复制到 lyedu-pc 的 `public/pptist/` 目录（若目录不存在请先创建）。
5. 启动或构建 lyedu-pc 后，访问「PPT 制作」页面即可在 iframe 内使用 PPTist。

若将 PPTist 部署到独立地址（如 `https://ppt.example.com`），可在 lyedu-pc 的 `.env` 中设置 `VITE_PPTIST_URL=https://ppt.example.com`，页面将优先使用该地址作为 iframe 的 `src`。

**注意**：PPTist 采用 AGPL-3.0 协议，商业使用请遵守协议或联系作者获取授权。

## 项目结构

```
lyedu-pc/
├── public/                 # 静态资源（favicon、图标等）
├── src/
│   ├── api/                # 接口封装
│   │   ├── auth.ts         # 登录、飞书
│   │   ├── config.ts       # 系统配置（site/player）
│   │   ├── course.ts       # 课程、分类、评论
│   │   ├── user.ts         # 用户信息、个人资料
│   │   ├── image.ts        # 图片上传（头像等）
│   │   ├── learning.ts     # 学习记录、加入课程、进度
│   │   ├── video.ts        # 视频
│   │   ├── exam.ts / point.ts / task.ts 等
│   ├── components/        # 公共组件
│   │   └── AppHeader.vue   # 顶栏（Logo、菜单、用户下拉）
│   ├── router/             # 路由与守卫
│   ├── utils/              # 工具（request、theme、auth）
│   └── views/              # 页面
├── .env.example
├── Dockerfile
├── nginx.conf
├── vite.config.ts
└── package.json
```

## 功能模块说明

### 已实现功能概览

| 模块 | 说明 |
|------|------|
| **首页** | Banner（站点标题来自后台配置）、最近学习、推荐课程、功能简介 |
| **登录** | 账号密码登录、飞书扫码登录（可配置）；登录页从后台加载 Logo、标题、主题 |
| **课程中心** | 课程列表、分页；关键词搜索、分类下拉筛选；加入课程、跳转详情 |
| **课程详情** | 课程信息、章节/视频列表、评论、附件；学习进度展示 |
| **视频播放** | 播放、进度保存、播放心跳；禁止拖拽/禁止倍速由后台配置控制 |
| **我的学习** | 已学课程与进度 |
| **知识中心** | 文档列表、分类；在线预览 |
| **考试中心** | 考试列表、答题、交卷、成绩与结果页 |
| **我的证书** | 证书列表、打印页 |
| **我的任务** | 任务列表与详情 |
| **积分** | 积分与排行榜 |
| **PPT 制作** | 集成 PPTist，在线编辑/演示 PPT（需自建 PPTist 静态资源，见下文） |
| **个人中心** | 查看/编辑昵称、头像、邮箱、手机；头像支持本地上传（POST /image/upload） |
| **使用说明** | 静态帮助页，入口在顶栏问号图标 |
| **全局** | 非登录页也应用后台主题（Logo/主题色）；路由 meta 设置页面标题；Header 用户区下拉（个人信息、退出） |

### 顶栏与路由

- **顶栏**：Logo（点击回首页）、首页 / 课程中心 / 学习与考试（知识中心、考试中心、我的任务、PPT 制作）/ 我的（我的学习、我的证书、积分）/ 右侧问号（使用说明）；未登录显示「登录」，已登录显示用户头像（或站点 Logo）+ 用户名下拉（个人信息、退出登录）。
- **路由**：见 `src/router/index.ts`；需登录页面带 `meta.requiresAuth: true`，未登录会跳转登录页并带 `redirect` 参数。

## 配置说明

### 后台系统配置（lyedu-admin 或 API）

学员端会读取以下配置键，用于展示与行为：

| 配置键 | 说明 | 使用位置 |
|--------|------|----------|
| `site.title` | 站点名称 | 登录页标题、首页 Banner、document.title 等 |
| `site.logo` | 站点 Logo 地址 | 登录页、Header 用户区（无用户头像时） |
| `site.theme_mode` | 主题模式 | auto / default / custom |
| `site.theme_color` | 主题色（theme_mode 为 custom 时） | 全局主题 |
| `player.disable_seek` | 是否禁止拖拽进度条 | 视频播放页 |
| `player.disable_speed` | 是否禁止倍速 | 视频播放页 |

### 前端环境变量

见上文「环境变量」；API 基路径在 `src/utils/request.ts` 中为 `/api`，开发时由 Vite 代理到后端，生产由 nginx 转发。

## 与后端、管理端的关系

- **lyedu-api-python**：提供 REST API（`/api` 前缀）；学员端所有数据与鉴权均通过该后端。
- **lyedu-admin**：管理后台，负责课程、用户、考试、系统配置等维护；学员端不直连管理端，仅通过共用后端间接使用配置与数据。

## 功能完善计划与完成情况

### 一、已有且较完整（上线前已具备）

- 首页、课程中心、课程详情、课程评论  
- 视频播放、学习进度、播放心跳  
- 我的学习、知识中心、文档预览  
- 考试、证书、任务、积分（含排行）  
- 登录（账号密码 + 飞书）、退出  
- 登录页从 config 加载 Logo / 标题 / 主题  

### 二、待完善功能（计划项，已全部实现）

| 功能 | 说明 | 状态 |
|------|------|------|
| 个人中心 | 查看/编辑资料，用户名点击进入 | ✅ |
| 课程中心搜索与筛选 | 关键词、分类下拉 | ✅ |
| 播放器配置 | 禁止拖拽、禁止倍速从配置读取 | ✅ |
| 全局主题 | 非登录页也应用 Logo/主题 | ✅ |
| 帮助/使用说明 | 学员端说明页 | ✅ |
| 用户信息 API / Header 用户区 | getCurrentUser、头像与下拉 | ✅ |

### 三、后续计划（P3，已实现）

| 项 | 说明 | 状态 |
|----|------|------|
| /user/info 返回 avatar | Header 显示用户头像 | ✅ |
| 课程分类列表 + 分类下拉 | GET /course/category | ✅ |
| 页面标题 | 路由 meta 设置 document.title | ✅ |
| 首页优化 | Banner 使用 site.title | ✅ |
| 个人中心头像上传 | POST /image/upload + el-upload | ✅ |

---

如需扩展登录方式（如企业微信、钉钉），可参考 `src/utils/auth.ts` 与登录页逻辑，并在后端增加对应鉴权接口。
