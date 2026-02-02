# LyEdu API Python - 使用国内镜像安装依赖
# 在 PowerShell 中执行: .\install.ps1

$ErrorActionPreference = "Stop"
$mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"

Write-Host "1. 创建虚拟环境 (python -m venv venv) ..."
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "若本机用 py 启动器，请改为: py -3 -m venv venv"
    exit 1
}

Write-Host "2. 激活虚拟环境并安装依赖 (清华源) ..."
& ".\venv\Scripts\pip.exe" install -r requirements.txt -i $mirror

Write-Host "完成。激活环境: .\venv\Scripts\Activate.ps1  启动: uvicorn main:app --host 0.0.0.0 --port 9700"
