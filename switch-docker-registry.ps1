# 自动轮换国内镜像前缀，找到可用的 JDK25 镜像源
#
# 用法：
#   cd D:\Users\73559\IdeaProjects\LyEdu
#   .\switch-docker-registry.ps1
# 然后：
#   docker-compose build --no-cache api
#   docker-compose up -d

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LyEdu - 自动选择可用镜像前缀" -ForegroundColor Cyan
Write-Host "目标：JDK 25（eclipse-temurin:25-jre-jammy）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 需要测试的“前缀”（必须以 / 结尾）
# 说明：本项目 Dockerfile 里使用 ${DOCKER_REGISTRY}library/<image>:<tag>
$candidates = @(
  "docker.m.daocloud.io/",
  "dockerproxy.com/",
  "registry.cn-hangzhou.aliyuncs.com/",
  "mirror.ccs.tencentyun.com/",
  "hub-mirror.c.163.com/",
  "docker.nju.edu.cn/"
)

$testRef = "library/eclipse-temurin:25-jre-jammy"

function Test-Pull([string]$prefix) {
  $img = "$prefix$testRef"
  Write-Host "测试: docker pull $img" -ForegroundColor Yellow
  docker pull $img | Out-Null
  return $LASTEXITCODE -eq 0
}

$ok = $null
foreach ($p in $candidates) {
  try {
    if (Test-Pull $p) { $ok = $p; break }
    Write-Host "  ✗ 失败" -ForegroundColor Red
  } catch {
    Write-Host "  ✗ 失败：$($_.Exception.Message)" -ForegroundColor Red
  }
  Write-Host ""
}

if (-not $ok) {
  Write-Host ""
  Write-Host "未找到可用镜像前缀。" -ForegroundColor Red
  Write-Host "你可以把公司/学校提供的镜像仓库前缀发我，我再加进候选列表。" -ForegroundColor Yellow
  exit 1
}

Write-Host ""
Write-Host "✅ 可用镜像前缀：" -ForegroundColor Green
Write-Host "  $ok" -ForegroundColor Green
Write-Host ""

$envPath = Join-Path (Get-Location) ".env"
if (-not (Test-Path $envPath)) {
  Write-Host "未找到 .env，先创建一个。" -ForegroundColor Yellow
  New-Item -ItemType File -Path $envPath | Out-Null
}

$content = Get-Content $envPath -Raw
if ($content -match "(?m)^DOCKER_REGISTRY=.*$") {
  $content = [regex]::Replace($content, "(?m)^DOCKER_REGISTRY=.*$", "DOCKER_REGISTRY=$ok")
} else {
  $content = "DOCKER_REGISTRY=$ok`r`n" + $content
}
Set-Content -Path $envPath -Value $content -Encoding UTF8

Write-Host "已写入 .env：" -ForegroundColor Green
Write-Host "  DOCKER_REGISTRY=$ok" -ForegroundColor Green
Write-Host ""

Write-Host "下一步执行：" -ForegroundColor Cyan
Write-Host "  docker-compose build --no-cache api" -ForegroundColor White
Write-Host "  docker-compose up -d" -ForegroundColor White
Write-Host ""

