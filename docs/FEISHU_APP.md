# 飞书内嵌与扫码登录

H5/PC 端可嵌套在飞书工作台内，点击应用直接进入；也支持在浏览器中通过飞书扫码登录。企业微信、钉钉等暂不实现，但前端与后端已预留扩展方式。

## 1. 飞书开放平台配置

1. 登录 [飞书开放平台](https://open.feishu.cn/app/) 创建自建应用，获取 **App ID**、**App Secret**。
2. **安全设置** → **重定向 URL**：配置前端回调地址，例如：
   - PC：`https://your-domain.com/login` 或 `https://your-domain.com/`（飞书会带上 `?code=xxx`）
   - H5：`https://your-domain.com/h5/login` 或对应 H5 入口
   - 内嵌时：配置实际打开的应用入口 URL（如 `https://your-domain.com/`、`https://your-domain.com/courses`）
3. **网页应用**（若使用）：配置桌面端/移动端主页 URL 为上述入口；内嵌在飞书内打开时，可在此 URL 上追加 `?from=feishu` 便于前端识别内嵌环境。

## 2. 后端配置

### Java（lyedu-api）

在 `application.yml` 或环境变量中配置：

```yaml
lyedu:
  feishu:
    app-id: ${FEISHU_APP_ID:}
    app-secret: ${FEISHU_APP_SECRET:}
    redirect-uri: ${FEISHU_REDIRECT_URI:}  # 可选，与前端回调一致
```

或环境变量：`FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_REDIRECT_URI`。

### Python（lyedu-api-python）

环境变量：`FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_REDIRECT_URI`（与 Java 含义一致）。

## 3. 前端登录方式（扩展点）

通过环境变量 `VITE_AUTH_PROVIDER` 控制（构建时注入）：

| 值 | 说明 |
|----|------|
| `local` | 仅账号密码登录（默认） |
| `feishu` | 仅飞书扫码/免登，不显示账号密码 |
| `both` | 飞书扫码 + 账号密码 |

- **PC**：在 `lyedu-pc` 下创建 `.env` 或 `.env.production`，例如 `VITE_AUTH_PROVIDER=feishu`。
- **H5**：在 `lyedu-h5` 下同理。

后续扩展企业微信、钉钉时，可在此增加 `wecom`、`dingtalk` 等，并在 `src/utils/auth.ts` 中增加对应判断与 API 调用。

## 4. 内嵌飞书时的行为

- **从飞书工作台打开应用**：入口 URL 建议带 `?from=feishu`（在飞书应用配置的主页 URL 中写死或由飞书注入）。前端检测到 `from=feishu` 且未登录且需鉴权时，会跳转到飞书授权页；用户授权后飞书重定向回当前页并带上 `code`，前端用 `code` 调后端 `/auth/feishu/callback` 换 JWT，写入本地后直接进入应用，无需再看到登录页。
- **在浏览器中打开**：访问需登录的页面会进入登录页；若 `VITE_AUTH_PROVIDER` 为 `feishu` 或 `both`，可点击「飞书扫码登录」跳转飞书授权页，扫码后同样通过 `code` 换 JWT 并进入应用。

## 5. 接口说明（与扩展预留）

- `GET /api/auth/feishu/url?redirect_uri=xxx&state=xxx`：获取飞书授权页 URL，前端跳转后用户扫码/确认，飞书重定向到 `redirect_uri?code=xxx&state=xxx`。
- `POST /api/auth/feishu/callback`，Body：`{ "code": "xxx", "redirectUri": "xxx" }`：用 code 换用户信息，查找或创建用户，返回 `{ "token", "userInfo" }`。

后端仅实现飞书；后续若有钉钉、企业微信，可增加 `/api/auth/dingtalk/*`、`/api/auth/wecom/*`，前端在 `auth.ts` 中按 `VITE_AUTH_PROVIDER` 或配置调用对应接口。
