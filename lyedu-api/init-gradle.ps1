# Initialize Gradle Wrapper (Windows)
# 在 lyedu-api 目录下执行: .\init-gradle.ps1
$ErrorActionPreference = "Stop"

$GradleVersion = "9.1.0"
$WrapperJarUrl = "https://raw.githubusercontent.com/gradle/gradle/v$GradleVersion/gradle/wrapper/gradle-wrapper.jar"
$DefaultDistUrl = "https://mirrors.cloud.tencent.com/gradle/gradle-$GradleVersion-bin.zip"

Write-Host "Initializing Gradle Wrapper..." -ForegroundColor Cyan
$apiDir = $PSScriptRoot
Set-Location $apiDir

New-Item -ItemType Directory -Force -Path "gradle\wrapper" | Out-Null

$propsPath = "gradle\wrapper\gradle-wrapper.properties"
if (Test-Path $propsPath) { $props = Get-Content $propsPath -Raw } else { $props = "" }
if ($props -notmatch "(?m)^distributionUrl=") {
  $props = "distributionBase=GRADLE_USER_HOME`ndistributionPath=wrapper/dists`ndistributionUrl=$DefaultDistUrl`nnetworkTimeout=10000`nvalidateDistributionUrl=true`nzipStoreBase=GRADLE_USER_HOME`nzipStorePath=wrapper/dists"
} else {
  $props = [regex]::Replace($props, "(?m)^distributionUrl=.*$", "distributionUrl=$DefaultDistUrl")
}
Set-Content -Path $propsPath -Value $props -Encoding UTF8

$jarPath = "gradle\wrapper\gradle-wrapper.jar"
if (-not (Test-Path $jarPath)) {
  Write-Host "Downloading gradle-wrapper.jar..." -ForegroundColor Yellow
  Invoke-WebRequest -Uri $WrapperJarUrl -OutFile $jarPath -UseBasicParsing
}

$gradlewBat = "gradlew.bat"
if (-not (Test-Path $gradlewBat)) {
  $bat = @'
@rem Gradle startup script for Windows
@echo off
setlocal
set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_HOME=%DIRNAME%
set CLASSPATH=%APP_HOME%gradle\wrapper\gradle-wrapper.jar
if defined JAVA_HOME (set JAVA_EXE=%JAVA_HOME%\bin\java.exe) else (set JAVA_EXE=java.exe)
"%JAVA_EXE%" %JAVA_OPTS% %GRADLE_OPTS% -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
endlocal
'@
  Set-Content -Path $gradlewBat -Value $bat -Encoding ASCII
}

$gradlew = "gradlew"
if (-not (Test-Path $gradlew)) {
  $sh = "#!/usr/bin/env sh`nDIRNAME=`$(dirname `"`$0`")`nAPP_HOME=`$(cd `"`$DIRNAME`" && pwd)`nCLASSPATH=`"`$APP_HOME/gradle/wrapper/gradle-wrapper.jar`"`nJAVA_CMD=`${JAVA_HOME:+`$JAVA_HOME/bin/}java`nexec `"`$JAVA_CMD`" `$JAVA_OPTS `$GRADLE_OPTS -classpath `"`$CLASSPATH`" org.gradle.wrapper.GradleWrapperMain `"`$@`""
  Set-Content -Path $gradlew -Value $sh -Encoding UTF8
}

$need = @("gradlew.bat", "gradle\wrapper\gradle-wrapper.jar", "gradle\wrapper\gradle-wrapper.properties")
$missing = @(); foreach ($f in $need) { if (-not (Test-Path $f)) { $missing += $f } }
if ($missing.Count -gt 0) {
  Write-Host "ERROR: Wrapper incomplete. Missing: $($missing -join ', ')" -ForegroundColor Red
  exit 1
}
Write-Host "Gradle Wrapper initialized." -ForegroundColor Green
Write-Host "Next: .\build-api.ps1" -ForegroundColor Cyan
