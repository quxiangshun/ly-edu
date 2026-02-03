# 提交信息避免中文乱码（Windows）

项目已配置 Git 使用 UTF-8 存储和输出提交信息：

- `i18n.commitEncoding = utf-8`
- `i18n.logOutputEncoding = utf-8`
- `core.quotepath = false`

在 Windows 下若仍出现中文乱码，可任选其一：

## 方式一：用文件写提交信息（推荐）

将提交信息写入文件并保存为 **UTF-8 编码**，再提交：

```powershell
# 用记事本/VSCode 等保存 msg.txt 为 UTF-8
git add .
git commit -F msg.txt
```

## 方式二：PowerShell 先切到 UTF-8 再提交

```powershell
chcp 65001
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
git add .
git commit -m "你的中文提交信息"
```

## 方式三：使用英文提交信息

例如：`feat: add task module`，可完全避免编码问题。
