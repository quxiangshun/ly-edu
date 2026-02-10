# lyedu-unix

LyEdu 学员端 uni-app x 版本，支持 H5 与微信小程序，功能与 lyedu-h5 保持一致。

## 技术栈

- uni-app x
- UTS / UVUE
- Vue 3 组合式 API

## 支持平台

- **H5**：浏览器访问
- **微信小程序**：需在 `manifest.json` 中配置 `mp-weixin.appid`

## 目录结构

```
lyedu-unix/
├── api/              # 接口封装（与 lyedu-h5 一致）
├── config/           # 配置
│   ├── api.uts       # API 基础地址
│   └── auth.uts      # 登录方式（local / feishu / both）
├── pages/            # 页面
├── static/           # 静态资源
├── utils/            # 工具（request、auth）
├── App.uvue
├── main.uts
├── pages.json
└── manifest.json
```

## 开发运行

使用 HBuilderX 打开本项目，或使用 uni-app x 官方 CLI 运行：

- **H5**：运行到浏览器
- **微信小程序**：运行到微信开发者工具

## API 配置

请求接口由 `config/api.uts` 中的 `API_BASE_URL` 控制。

### 开发环境（无代理）

若前端 dev server 未配置 `/api` 代理，请使用后端完整地址：

```
export const API_BASE_URL = 'http://localhost:9700/api'
```

需确保后端（lyedu-api-python 或 lyedu-api）已启动，默认端口 9700。

### 生产环境 / 已配置代理

若通过 Nginx 等同域代理，或 dev server 已配置 proxy，可使用相对路径：

```
export const API_BASE_URL = '/api'
```

## 登录方式

在 `config/auth.uts` 中设置：

- `local`：仅账号密码登录（默认）
- `feishu`：仅飞书扫码
- `both`：两者都支持

## 鉴权

- 未登录时自动跳转登录页，不登录无法访问任何内容
- Token 存储于本地，请求自动携带 `Authorization` 头
- 401 时清除登录态并跳转登录页

## 与 lyedu-h5 的关系

- 接口路径、参数、返回值与 lyedu-h5 相同
- 业务逻辑按 lyedu-h5 页面实现
- 后端共用 lyedu-api-python 或 lyedu-api
