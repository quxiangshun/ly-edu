# LyEdu API 构建脚本 (Windows)
# 在 lyedu-api 目录下执行: .\build-api.ps1
# 使用 Gradle 构建并将 JAR 复制到仓库根目录 pkg/

$ErrorActionPreference = "Stop"

# 使用 UTF-8 输出，避免 Gradle/Java 中文警告乱码
$OutputEncoding = [System.Text.Encoding]::UTF8
if ([Console]::OutputEncoding.CodePage -ne 65001) {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  chcp 65001 | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LyEdu API - Gradle Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$apiDir = $PSScriptRoot
$pkgDir = Join-Path (Split-Path $apiDir -Parent) "pkg"

if (-not (Test-Path $apiDir)) {
  Write-Host "ERROR: current directory invalid." -ForegroundColor Red
  exit 1
}

if (-not (Test-Path $pkgDir)) {
  New-Item -ItemType Directory -Path $pkgDir | Out-Null
  Write-Host "Created pkg/ directory." -ForegroundColor Green
}

Write-Host "Running: gradlew.bat bootJar (rerun tasks)" -ForegroundColor Cyan
Push-Location $apiDir
try {
  $gradlew = ".\gradlew.bat"
  if (-not (Test-Path $gradlew)) {
    Write-Host "ERROR: Gradle Wrapper not found." -ForegroundColor Red
    Write-Host "Run: .\init-gradle.ps1" -ForegroundColor Yellow
    exit 1
  }

  & $gradlew bootJar --rerun-tasks --no-build-cache
  if ($LASTEXITCODE -ne 0) { throw "Gradle build failed (bootJar)." }

  $jarPath = Join-Path $pkgDir "lyedu-api.jar"
  if (Test-Path $jarPath) {
    $fileInfo = Get-Item $jarPath
    Write-Host "OK: pkg\lyedu-api.jar" -ForegroundColor Green
    Write-Host ("Size: {0} MB" -f [math]::Round($fileInfo.Length / 1MB, 2)) -ForegroundColor Gray
  } else {
    throw "Expected jar not found at pkg\lyedu-api.jar"
  }
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "Next:" -ForegroundColor Cyan
Write-Host "  cd scripts/docker" -ForegroundColor White
Write-Host "  docker compose build api" -ForegroundColor White
Write-Host "  docker compose up -d" -ForegroundColor White
Write-Host ""
