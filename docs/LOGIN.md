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
| feishu | H5 浏览器 | 飞书扫码登录 |
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

### 2.5 流程

- **飞书 App 内**：点击「飞书授权登录」→ 跳转飞书授权页 → 授权后回调带 code → 后端换 token → 跳转个人中心
- **飞书 PC / H5**：展示二维码 → 用户飞书扫码 → 授权后回调带 code → 后端换 token → 登录成功

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
