# Initialize Gradle Wrapper (Windows)
# Goal: generate lyedu-api/gradlew(.bat) and gradle/wrapper/gradle-wrapper.jar
# This script DOES NOT require a pre-installed Gradle.

$ErrorActionPreference = "Stop"

$GradleVersion = "9.1.0"
$WrapperJarUrl = "https://raw.githubusercontent.com/gradle/gradle/v$GradleVersion/gradle/wrapper/gradle-wrapper.jar"

# China-friendly Gradle distribution mirror (Tencent Cloud)
$DefaultDistUrl = "https://mirrors.cloud.tencent.com/gradle/gradle-$GradleVersion-bin.zip"

Write-Host "Initializing Gradle Wrapper..." -ForegroundColor Cyan

$apiDir = Join-Path $PSScriptRoot "lyedu-api"
if (-not (Test-Path $apiDir)) {
  Write-Host "ERROR: lyedu-api directory not found." -ForegroundColor Red
  exit 1
}

Push-Location $apiDir
try {
  New-Item -ItemType Directory -Force -Path "gradle\wrapper" | Out-Null

  # 1) Ensure gradle-wrapper.properties uses CN mirror for distributionUrl
  $propsPath = "gradle\wrapper\gradle-wrapper.properties"
  if (Test-Path $propsPath) {
    $props = Get-Content $propsPath -Raw
  } else {
    $props = ""
  }

  if ($props -notmatch "(?m)^distributionUrl=") {
    $props = @"
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=$DefaultDistUrl
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"@
  } else {
    $props = [regex]::Replace($props, "(?m)^distributionUrl=.*$", "distributionUrl=$DefaultDistUrl")
  }
  Set-Content -Path $propsPath -Value $props -Encoding UTF8

  # 2) Download gradle-wrapper.jar
  $jarPath = "gradle\wrapper\gradle-wrapper.jar"
  if (-not (Test-Path $jarPath)) {
    Write-Host "Downloading gradle-wrapper.jar..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $WrapperJarUrl -OutFile $jarPath -UseBasicParsing
  }

  # 3) Create gradlew.bat (Windows)
  $gradlewBat = "gradlew.bat"
  if (-not (Test-Path $gradlewBat)) {
    @"
@rem -----------------------------------------------------------------------------
@rem Gradle startup script for Windows
@rem -----------------------------------------------------------------------------
@echo off
setlocal
set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

set DEFAULT_JVM_OPTS=

set CLASSPATH=%APP_HOME%gradle\wrapper\gradle-wrapper.jar

@rem Find java.exe
if defined JAVA_HOME (
  set JAVA_EXE=%JAVA_HOME%\bin\java.exe
) else (
  set JAVA_EXE=java.exe
)

"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
endlocal
"@ | Set-Content -Path $gradlewBat -Encoding ASCII
  }

  # 4) Create gradlew (for completeness)
  $gradlew = "gradlew"
  if (-not (Test-Path $gradlew)) {
@'
#!/usr/bin/env sh
DIRNAME=$(dirname "$0")
APP_HOME=$(cd "$DIRNAME" && pwd)
CLASSPATH="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"
JAVA_CMD=${JAVA_HOME:+$JAVA_HOME/bin/}java
exec "$JAVA_CMD" $JAVA_OPTS $GRADLE_OPTS -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
'@ | Set-Content -Path $gradlew -Encoding UTF8
  }

  # 5) Verify
  $need = @(
    "gradlew.bat",
    "gradle\wrapper\gradle-wrapper.jar",
    "gradle\wrapper\gradle-wrapper.properties"
  )
  $missing = @()
  foreach ($f in $need) { if (-not (Test-Path $f)) { $missing += $f } }
  if ($missing.Count -gt 0) {
    Write-Host "ERROR: Wrapper initialization incomplete. Missing:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
  }

  Write-Host "Gradle Wrapper initialized successfully." -ForegroundColor Green
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "Next: run backend packaging:" -ForegroundColor Cyan
Write-Host "  .\build-api.ps1" -ForegroundColor White
Write-Host ""
