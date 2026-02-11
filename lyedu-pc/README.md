# lyedu-pc

学员端 PC 前端，面向普通学员使用。管理后台为 lyedu-admin，后端 API 为 lyedu-api-python。

## 技术栈

- Vue 3 + TypeScript + Vite
- Element Plus
- Vue Router

## 开发

```bash
npm install
npm run dev
```

## 功能完善计划

根据 lyedu-api-python 与 lyedu-admin 的功能模块，对 lyedu-pc 的待完善项整理如下。

### 一、已有且较完整

- 首页、课程中心、课程详情、课程评论
- 视频播放、学习进度、播放心跳
- 我的学习、知识中心、文档预览
- 考试、证书、任务、积分（含排行）
- 登录（账号密码 + 飞书）、退出
- 登录页从 config 加载 Logo / 标题 / 主题

### 二、待完善功能

| 功能 | 说明 | API 支持 |
|------|------|----------|
| **1. 个人中心** | 查看/编辑个人资料（昵称、头像、邮箱、手机），用户名点击进入 | GET /user/info、PUT /user/{id} |
| **2. 课程中心搜索与筛选** | 关键词搜索、分类/标签筛选 | GET /course/page 支持 keyword、categoryId |
| **3. 播放器配置** | 从系统配置读取「禁止拖拽」「禁止倍速」并生效 | GET /config/key (player.disable_seek、player.disable_speed) |
| **4. 全局主题** | 进入非登录页时也应用 Logo/主题（目前仅登录页加载） | GET /config/key (site.logo、site.theme_mode、site.theme_color) |
| **5. 帮助/使用说明** | 学员端简要使用说明页面 | 无接口，静态内容或复用帮助说明 |
| **6. 用户信息 API** | 封装 getCurrentUser（/user/info），供 Header、个人中心等使用 | GET /user/info |
| **7. Header 用户区** | 用户名可点击跳转个人中心，头像展示（如有） | 依赖 getCurrentUser |

### 三、实施优先级

| 优先级 | 模块 | 备注 |
|--------|------|------|
| P0 | 播放器配置、全局主题 | 影响全局体验 |
| P1 | 个人中心、用户 API、Header 用户区 | 基础能力 |
| P2 | 课程搜索与筛选、帮助说明 | 体验增强 |

### 四、后续计划（P3）

| 项 | 说明 | 状态 |
|----|------|------|
| /user/info 返回 avatar | 便于 Header 显示用户头像 | ✅ 已实现 |
| 课程分类列表 API + 分类下拉 | GET /course/category，课程中心用下拉选分类 | ✅ 已实现 |
| 页面标题 | 路由切换时根据 meta.title 设置 document.title | ✅ 已实现 |
| 首页/课程页优化 | 可根据业务继续增强展示与交互 | 待定 |
| 个人中心头像上传 | 依赖后端上传接口 | 待定 |
