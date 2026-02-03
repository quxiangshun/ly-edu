# LyEdu API Python - 启动脚本（先执行 Alembic 迁移，再启动服务）
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Windows 下避免 Alembic/文件读取使用 GBK 导致解码错误
if ($env:PYTHONUTF8 -eq $null) { $env:PYTHONUTF8 = "1" }
# 若存在虚拟环境则使用，便于找到 alembic/uvicorn
if (Test-Path ".\.venv\Scripts\Activate.ps1") { .\.venv\Scripts\Activate.ps1 }

Write-Host "Running Alembic migrations..." -ForegroundColor Cyan
& alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Alembic upgrade failed (exit $LASTEXITCODE). Start anyway? [y/N]" -ForegroundColor Yellow
    $r = Read-Host
    if ($r -ne "y" -and $r -ne "Y") { exit $LASTEXITCODE }
}

Write-Host "Starting LyEdu API (uvicorn)..." -ForegroundColor Green
& uvicorn main:app --host $env:HOST --port $env:PORT --reload
