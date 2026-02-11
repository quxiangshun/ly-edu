# Font Awesome 图标

本目录图标来自 [Font Awesome](https://github.com/FortAwesome/Font-Awesome) 项目（CC BY 4.0 许可）。

## 图标列表

| 文件 | 用途 |
|------|------|
| house.svg | 首页（TabBar） |
| book.svg | 课程（TabBar） |
| user.svg | 我的（TabBar） |
| book-open.svg | 知识中心、课程学习 |
| play.svg | 视频播放、我的学习 |
| thumbs-up.svg | 我点赞的视频 |
| coins.svg | 我的积分 |
| certificate.svg | 我的证书 |
| list-check.svg | 我的任务 |
| file-lines.svg | 考试中心 |
| gear.svg | 设置 |
| circle-info.svg | 关于 |

## 使用方式

### 在 uvue 页面中

```html
<image src="/static/icons/fontawesome/house.svg" class="icon" />
```

### TabBar 说明

uni-app TabBar 的 `iconPath` 需使用 PNG/JPG 图片。若需使用本目录图标作为 TabBar 图标，可将 SVG 转为 PNG 后放到 `static/` 下，并在 `pages.json` 中配置。

## 添加更多图标

从 [Font Awesome](https://github.com/FortAwesome/Font-Awesome) 仓库的 `svgs/solid/` 或 `svgs/regular/` 目录下载所需 SVG，保存到本目录即可。
