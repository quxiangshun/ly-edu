# LyEdu API Python - 启动脚本（先执行 Alembic 迁移，再启动服务）
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Running Alembic migrations..." -ForegroundColor Cyan
& alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Alembic upgrade failed (exit $LASTEXITCODE). Start anyway? [y/N]" -ForegroundColor Yellow
    $r = Read-Host
    if ($r -ne "y" -and $r -ne "Y") { exit $LASTEXITCODE }
}

Write-Host "Starting LyEdu API (uvicorn)..." -ForegroundColor Green
& uvicorn main:app --host $env:HOST --port $env:PORT --reload
