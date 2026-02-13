# LyEdu 开发环境一键停止（关闭由 start.ps1 启动的终端及服务）
# 建议在项目根目录执行: .\scripts\dev\stop.ps1
$ErrorActionPreference = "SilentlyContinue"
$ScriptDir = $PSScriptRoot
$Root = (Resolve-Path (Join-Path (Join-Path $ScriptDir "..") "..")).Path
Set-Location $Root

$ServersFile = Join-Path $Root ".dev-servers.json"

# 1. 按 PID 关闭 start.ps1 打开的终端窗口
if (Test-Path $ServersFile) {
    $data = Get-Content $ServersFile -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($w in $data.windows) {
        $pid = $w.pid
        $name = $w.name
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "已关闭: $name (PID $pid)" -ForegroundColor Green
        } catch {
            Write-Host "关闭 $name (PID $pid) 失败或已退出" -ForegroundColor Gray
        }
    }
    Remove-Item $ServersFile -Force
}

# 2. 按端口结束可能残留的进程（用户手动关终端后服务可能仍在）
$ports = @(9700, 9800, 9900)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        $pids = $conn.OwningProcess | Sort-Object -Unique
        foreach ($pid in $pids) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "已结束端口 $port 上的进程 (PID $pid)" -ForegroundColor Yellow
            } catch { }
        }
    }
}

Write-Host "开发环境已停止。" -ForegroundColor Cyan
