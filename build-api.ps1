# LyEdu API build script (Windows)
# Build with Gradle and copy JAR to root pkg/ folder.

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LyEdu API - Gradle Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$apiDir = Join-Path $PSScriptRoot "lyedu-api"
$pkgDir = Join-Path $PSScriptRoot "pkg"

if (-not (Test-Path $apiDir)) {
  Write-Host "ERROR: lyedu-api directory not found." -ForegroundColor Red
  exit 1
}

if (-not (Test-Path $pkgDir)) {
  New-Item -ItemType Directory -Path $pkgDir | Out-Null
  Write-Host "Created pkg/ directory." -ForegroundColor Green
}

Write-Host "Entering lyedu-api..." -ForegroundColor Yellow
Push-Location $apiDir
try {
  $gradlew = ".\\gradlew.bat"
  if (-not (Test-Path $gradlew)) {
    Write-Host "ERROR: Gradle Wrapper not found." -ForegroundColor Red
    Write-Host ("Current dir: {0}" -f (Get-Location)) -ForegroundColor Yellow
    Write-Host "Files in current dir:" -ForegroundColor Yellow
    Get-ChildItem -Force | Select-Object -First 20 | ForEach-Object { Write-Host ("  - {0}" -f $_.Name) -ForegroundColor Yellow }
    Write-Host "Run: .\\init-gradle.ps1" -ForegroundColor Yellow
    exit 1
  }

  Write-Host "Running: gradlew.bat bootJar (rerun tasks)" -ForegroundColor Cyan
  & $gradlew bootJar --rerun-tasks --no-build-cache
  if ($LASTEXITCODE -ne 0) { throw "Gradle build failed (bootJar)." }

  $jarPath = Join-Path $pkgDir "lyedu-api.jar"
  if (Test-Path $jarPath) {
    $fileInfo = Get-Item $jarPath
    Write-Host "OK: pkg\\lyedu-api.jar" -ForegroundColor Green
    Write-Host ("Size: {0} MB" -f [math]::Round($fileInfo.Length / 1MB, 2)) -ForegroundColor Gray
  } else {
    throw "Expected jar not found at pkg\\lyedu-api.jar"
  }
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "Next:" -ForegroundColor Cyan
Write-Host "  docker-compose build api" -ForegroundColor White
Write-Host "  docker-compose up -d" -ForegroundColor White
Write-Host ""
