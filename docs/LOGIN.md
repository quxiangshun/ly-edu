# 多平台登录说明

LyEdu 支持飞书、钉钉、企微三种企业平台登录（**三选一**），以及微信小程序手机号登录、账号密码登录。平台由管理后台配置 `app.platform`，前端自动识别，不写死平台名称。

---

## 一、平台配置

### 1.1 配置项

| 配置键 | 可选值 | 说明 |
|--------|--------|------|
| `app.platform` | `feishu` \| `dingtalk` \| `wecom` \| `wechat_mp` \| `local` | 应用发布平台（唯一） |
| `app.redirect_uri` | URL 字符串 | OAuth 回调基础 URL，H5 可留空由前端自动检测 |

在 `ly_config` 表中设置，或通过管理后台「系统设置」配置。

### 1.2 运行场景与登录方式

| 发布平台 | 运行环境 | 登录方式 |
|----------|----------|----------|
| feishu | 飞书 App（手机） | 飞书授权登录 → 跳转个人中心 |
| feishu | 飞书 PC | 飞书扫码登录 |
| feishu | H5 浏览器 | 飞书扫码登录 + 账号密码登录 |
| dingtalk | 钉钉 App / PC / H5 | 钉钉授权 / 扫码（预留） |
| wecom | 企微 App / PC / H5 | 企微授权 / 扫码（预留） |
| wechat_mp | 微信小程序 | 获取手机号 → 校验用户 → 绑定 union_id |
| local | 任意 | 仅账号密码登录 |

---

## 二、飞书登录

### 2.1 开放平台配置

1. 登录 [飞书开放平台](https://open.feishu.cn/app/) 创建自建应用
2. 获取 **App ID**、**App Secret**
3. **安全设置** → **重定向 URL**：配置回调地址，例如：
   - `https://your-domain.com/h5/`
   - `https://your-domain.com/#/pages/login/login`
4. **权限管理**：申请「以应用身份读取通讯录」等所需权限

### 2.2 后端配置（lyedu-api-python）

在 `.env` 或环境变量中配置：

```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_REDIRECT_URI=https://your-domain.com/h5/   # 可选，与重定向 URL 一致
```

### 2.3 管理后台配置

- `app.platform` = `feishu`
- `app.redirect_uri` = 前端登录页完整 URL（H5 可留空）

### 2.4 接口说明

| 接口 | 说明 |
|------|------|
| `GET /api/auth/platform-info` | 获取平台配置（platform、authLabel） |
| `GET /api/auth/feishu/url?redirect_uri=xxx&device=mobile\|pc` | 获取飞书授权 URL；device=pc 时返回 qrcodeGoto |
| `GET /api/auth/feishu/qrcode?redirect_uri=xxx` | 获取飞书扫码登录用 goto URL |
| `POST /api/auth/feishu/callback` | Body: `{ code, redirectUri }`，用 code 换 token |

### 2.5 三种登录方式详细操作步骤

#### 2.5.1 飞书 App（手机端）— 授权登录

**适用**：将 lyedu-unix 发布为飞书微应用，用户在飞书手机端打开应用。

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 飞书开放平台创建应用 | 登录 [open.feishu.cn](https://open.feishu.cn/app/)，创建「企业自建」应用，记录 App ID、App Secret |
| 2 | 配置重定向 URL | 安全设置 → 重定向 URL，添加：`https://your-domain.com/h5/` 或实际 H5 部署地址（需与前端回调一致） |
| 3 | 申请权限 | 权限管理 → 添加「以应用身份读取通讯录」「获取用户 userid」等 |
| 4 | 发布应用到飞书 | 版本管理与发布 → 创建版本 → 网页应用，填写桌面端/移动端主页 URL（同上） |
| 5 | 后端配置 `.env` | `FEISHU_APP_ID=xxx`、`FEISHU_APP_SECRET=xxx`、`FEISHU_REDIRECT_URI=https://your-domain.com/h5/` |
| 6 | 数据库配置 | `ly_config` 表中 `app.platform` = `feishu` |
| 7 | 前端构建 H5 | 将 lyedu-unix 构建为 H5，部署到 `https://your-domain.com/h5/` |
| 8 | 飞书工作台添加应用 | 管理员在飞书管理后台将应用添加到工作台，员工从工作台进入 |
| 9 | 用户操作 | 点击应用 → 未登录时进入登录页 → 点击「飞书授权登录」→ 跳转飞书授权确认 → 确认后自动回到个人中心 |

**技术要点**：`redirect_uri` 必须与飞书应用配置的重定向 URL 完全一致；前端检测到 `runPlatform === 'feishu_app'` 时展示授权按钮，点击后通过 `window.location.href` 跳转飞书授权页，回调时 URL 带 `?code=xxx`，前端解析 code 调用 `POST /api/auth/feishu/callback` 换 token。

---

#### 2.5.2 飞书 PC — 扫码登录

**适用**：用户在飞书 PC 客户端内打开应用（或通过飞书工作台进入）。

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 同 2.5.1 步骤 1～3 | 飞书应用创建、重定向 URL、权限 |
| 2 | 重定向 URL 配置 | 确保 PC 端打开时的实际 URL 在重定向白名单中，如 `https://your-domain.com/h5/#/pages/login/login` |
| 3 | 后端配置 | 同 2.5.1 步骤 5 |
| 4 | 数据库配置 | `app.platform` = `feishu` |
| 5 | 前端逻辑 | 检测到 `runPlatform === 'feishu_pc'` 时展示扫码区域 |
| 6 | 获取二维码 | 调用 `GET /api/auth/feishu/qrcode?redirect_uri=xxx` 获取 goto URL，用第三方服务生成二维码图片（如 `https://api.qrserver.com/v1/create-qr-code/?data=xxx`） |
| 7 | 用户操作 | 使用飞书 App 扫描页面上的二维码 → 在手机端确认授权 → PC 页面轮询或刷新，检测到 URL 带 `code` 后调用 callback 换 token |

**技术要点**：飞书 PC 端实际运行 H5，与手机端共用同一套前端；区别在于 `uni.getSystemInfoSync().platform` 为 `windows`/`mac` 时识别为 `feishu_pc`，展示扫码 UI 而非授权按钮。

---

#### 2.5.3 H5 浏览器 — 扫码登录

**适用**：用户在普通浏览器（Chrome、Safari 等）访问 H5 地址，非飞书客户端内。默认展示扫码区域，二维码底部有小字「账号密码登录」可切换至账号密码表单；在账号密码表单顶部有小字「飞书/钉钉/企微 扫码登录」可切换回扫码。

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 同 2.5.1 步骤 1～3 | 飞书应用、重定向 URL、权限 |
| 2 | 重定向 URL | 添加浏览器实际访问的登录页地址，如 `https://your-domain.com/h5/#/pages/login/login` 或 `https://your-domain.com/` |
| 3 | 后端配置 | 同 2.5.1 步骤 5，`FEISHU_REDIRECT_URI` 与重定向 URL 一致 |
| 4 | 可选：配置 `app.redirect_uri` | 在 `ly_config` 中配置，如 `https://your-domain.com/h5/`，用于构造回调；不配置时 H5 会从 `location.origin + location.pathname` 自动获取 |
| 5 | 前端逻辑 | 检测到 `runPlatform === 'h5'` 且 `platform === 'feishu'` 时展示扫码区域 |
| 6 | 加载二维码 | 调用 `GET /api/auth/feishu/qrcode?redirect_uri=xxx`，`redirect_uri` = `app.redirect_uri` 或 `location.origin + pathname` + `?redirect=目标页` |
| 7 | 用户操作 | 打开飞书 App → 扫描页面二维码 → 在飞书内确认授权 → 飞书会打开回调 URL（需在手机浏览器或飞书内置浏览器中完成），带回 `code` |
| 8 | 回调处理 | 登录页 URL 带 `?code=xxx` 时，`onLoad` 中解析 code，调用 `POST /api/auth/feishu/callback` 换 token，成功后跳转个人中心 |

**技术要点**：H5 扫码场景下，用户扫码后可能在手机浏览器或飞书内打开回调页；若在飞书内打开，相当于飞书 App 内流程，可直接拿 code 换 token；若在手机浏览器打开，需确保该 URL 与配置的重定向 URL 一致。

**注意事项**：

- 重定向 URL 必须与飞书开放平台配置的完全一致（含协议、域名、路径、尾部斜杠）
- 若 H5 使用 hash 路由（`#/pages/login/login`），重定向 URL 需包含 hash 或使用不带 hash 的入口
- 二维码有效期通常几分钟，可增加「刷新二维码」按钮

---

### 2.6 流程概览

- **飞书 App 内**：点击「飞书授权登录」→ 跳转飞书授权页 → 授权后回调带 code → 后端换 token → 跳转个人中心
- **飞书 PC / H5**：展示二维码 → 用户飞书扫码 → 授权后回调带 code → 后端换 token → 登录成功；H5 浏览器额外提供账号密码登录

---

## 三、钉钉登录

### 3.1 状态

**预留接口**，暂未实现。后端返回 501，待配置钉钉开放平台并实现后启用。

### 3.2 预留接口

| 接口 | 说明 |
|------|------|
| `GET /api/auth/dingtalk/url?redirect_uri=xxx` | 钉钉授权 URL |
| `GET /api/auth/dingtalk/qrcode` | 钉钉扫码登录 |
| `POST /api/auth/dingtalk/callback` | 钉钉授权回调 |

### 3.3 扩展步骤（后续）

1. 在钉钉开放平台创建应用，获取 AppKey、AppSecret
2. 配置 `.env`：`DINGTALK_APP_KEY`、`DINGTALK_APP_SECRET`
3. 实现 `util/dingtalk_api.py`，对接钉钉 OAuth / 扫码
4. 在 `routers/auth.py` 中实现上述接口
5. 管理后台设置 `app.platform` = `dingtalk`

---

## 四、企微登录

### 4.1 状态

**预留接口**，暂未实现。后端返回 501，待配置企业微信开放平台并实现后启用。

### 4.2 预留接口

| 接口 | 说明 |
|------|------|
| `GET /api/auth/wecom/url?redirect_uri=xxx` | 企微授权 URL |
| `GET /api/auth/wecom/qrcode` | 企微扫码登录 |
| `POST /api/auth/wecom/callback` | 企微授权回调 |

### 4.3 扩展步骤（后续）

1. 在企业微信管理后台创建自建应用，获取 AgentId、Secret
2. 配置 `.env`：`WECOM_CORP_ID`、`WECOM_AGENT_ID`、`WECOM_SECRET`
3. 实现 `util/wecom_api.py`，对接企微 OAuth / 扫码
4. 在 `routers/auth.py` 中实现上述接口
5. 管理后台设置 `app.platform` = `wecom`

---

## 五、微信小程序登录

### 5.1 流程

1. 用户进入小程序，点击「获取手机号登录」
2. 授权后获取 `getPhoneNumber` 返回的 `code`
3. 前端调用 `POST /api/auth/wechat-mp/phone`，传递 `code` 与 `wx.login` 的 `code`
4. 后端用 `code` 换取手机号，根据手机号查询用户
5. 若用户存在：绑定 `union_id`（或 openid），返回 token
6. 若用户不存在：返回「用户不存在」

### 5.2 后端配置

```bash
WECHAT_MP_APP_ID=your_mp_appid
WECHAT_MP_APP_SECRET=your_mp_secret
```

### 5.3 接口说明

| 接口 | 说明 |
|------|------|
| `POST /api/auth/wechat-mp/phone` | Body: `{ code, phoneCode }`，手机号校验并绑定 union_id |

### 5.4 数据说明

- 数据库 `ly_user` 使用 `union_id` 存储微信开放平台 unionid（同主体多应用统一）
- 用户需预先在系统中存在（如通过飞书同步、管理后台创建），且 `mobile` 与授权手机号一致

---

## 六、账号密码登录

### 6.1 配置

设置 `app.platform` = `local`，仅展示用户名、密码表单。

### 6.2 接口

| 接口 | 说明 |
|------|------|
| `POST /api/auth/login` | Body: `{ username, password }`，返回 token、userInfo |

---

## 七、前端逻辑（lyedu-unix）

- `utils/platform.uts`：检测运行环境（feishu_app、feishu_pc、wechat_mp、h5）
- `pages/login/login.uvue`：根据 `getPlatformInfo()` 与运行环境动态展示对应登录方式
- 按钮文案使用 `authLabel`（飞书/钉钉/企微），不写死平台名称
