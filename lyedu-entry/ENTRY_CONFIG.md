# 统一入口配置：从入口页跳转到 H5 或 PC 端

统一入口项目 `lyedu-entry` 提供单页，根据**链接选择**或**设备/参数**跳转到 PC 端、H5 端或管理后台。

## 1. 环境变量（构建时）

在 `lyedu-entry` 目录下创建 `.env` 或 `.env.production`，参考 `.env.example`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `VITE_PC_URL` | PC 端地址 | `/pc/` |
| `VITE_H5_URL` | H5 端地址 | `/h5/` |
| `VITE_ADMIN_URL` | 管理后台地址 | `/admin/` |
| `VITE_AUTO_REDIRECT` | 是否按设备自动跳转（手机→H5，电脑→PC） | 不设或 `false` |

- **同域部署**：用相对路径即可，如 `VITE_PC_URL=/pc/`、`VITE_H5_URL=/h5/`、`VITE_ADMIN_URL=/admin/`。
- **不同域**：填完整 URL，如 `VITE_PC_URL=https://pc.your-domain.com/`、`VITE_H5_URL=https://h5.your-domain.com/`。

修改后需重新构建：`npm run build`。

## 2. 跳转方式

### 方式一：页面点击（默认）

访问统一入口页（如 `https://your-domain.com/`），会看到三个按钮：

- **PC 端** → 跳转到 `VITE_PC_URL`
- **H5 端** → 跳转到 `VITE_H5_URL`
- **管理后台** → 跳转到 `VITE_ADMIN_URL`

### 方式二：URL 参数强制指定端

在入口 URL 后加 `?t=pc`、`?t=h5` 或 `?t=admin`，进入后**直接跳转**，不显示选择页：

- `https://your-domain.com/?t=pc` → PC 端
- `https://your-domain.com/?t=h5` → H5 端
- `https://your-domain.com/?t=admin` → 管理后台

适合在飞书/企业微信里配置固定链接（如 H5 用 `?t=h5`）。

### 方式三：按设备自动跳转

设置 `VITE_AUTO_REDIRECT=true` 并重新构建后：

- 访问入口页且**没有** `?t=xxx` 时，会根据设备自动跳转：
  - 手机/平板（根据 User-Agent）→ H5 端
  - 电脑 → PC 端
- 若有 `?t=pc` / `?t=h5` / `?t=admin`，仍以参数为准。

## 3. 同域 Nginx 部署示例

同一域名下，入口、PC、H5、管理后台用路径区分时，可类似配置：

```nginx
server {
  listen 80;
  server_name your-domain.com;
  root /var/www/lyedu;

  # 统一入口（根路径）
  location / {
    alias /var/www/lyedu/entry/dist/;
    try_files $uri $uri/ /index.html;
  }

  # PC 端
  location /pc/ {
    alias /var/www/lyedu/pc/dist/;
    try_files $uri $uri/ /pc/index.html;
  }

  # H5 端
  location /h5/ {
    alias /var/www/lyedu/h5/dist/;
    try_files $uri $uri/ /h5/index.html;
  }

  # 管理后台
  location /admin/ {
    alias /var/www/lyedu/admin/dist/;
    try_files $uri $uri/ /admin/index.html;
  }

  # 后端 API（若同机）
  location /api/ {
    proxy_pass http://127.0.0.1:9700;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

构建时保持默认即可（`VITE_PC_URL=/pc/`、`VITE_H5_URL=/h5/`、`VITE_ADMIN_URL=/admin/`）。

## 4. 本地开发

- 入口：`cd lyedu-entry && npm run dev`（默认端口 9777）
- PC：`cd lyedu-pc && npm run dev`（9800）
- H5：`cd lyedu-h5 && npm run dev`（9801）
- 管理后台：`cd lyedu-admin && npm run dev`（9900）

本地用不同端口时，可在 `lyedu-entry` 的 `.env` 里写完整地址，例如：

```env
VITE_PC_URL=http://localhost:9800/
VITE_H5_URL=http://localhost:9801/
VITE_ADMIN_URL=http://localhost:9900/
```

这样从统一入口点击或带 `?t=pc` / `?t=h5` / `?t=admin` 会正确跳到对应端。
