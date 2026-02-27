# LyEdu API - 停止运行在指定端口的服务（默认 9700）
$Port = if ($env:PORT) { [int]$env:PORT } else { 9700 }

$found = $false

# 方式1：Get-NetTCPConnection（Windows 8+）
$conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $conn | ForEach-Object {
        $p = $_.OwningProcess
        Write-Host "[LyEdu] 正在停止 PID $p (端口 $Port) ..." -ForegroundColor Yellow
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        $found = $true
    }
}

# 方式2：备选通过进程名（lyedu_backend 或 python）
if (-not $found) {
    Get-Process -Name lyedu_backend -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "[LyEdu] 正在停止 lyedu_backend (PID $($_.Id)) ..." -ForegroundColor Yellow
        Stop-Process -Id $_.Id -Force
        $found = $true
    }
}

if ($found) {
    Write-Host "[LyEdu] 服务已停止" -ForegroundColor Green
} else {
    Write-Host "[LyEdu] 端口 $Port 上未发现运行中的服务" -ForegroundColor Gray
}
