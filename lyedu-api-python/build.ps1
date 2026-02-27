# LyEdu build.ps1 - Docker 构建 Linux 可执行文件
# 产出: lyedu-api-python/dist/lyedu_backend
# 使用: .\lyedu-api-python\build.ps1
# 国内网络默认使用清华镜像，直连 Docker Hub 可设: $env:DOCKER_REGISTRY=""

$ErrorActionPreference = "Stop"
$RepoRoot = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Split-Path (Get-Location) -Parent }
$DistDir = Join-Path $RepoRoot "lyedu-api-python\dist"
$DistFile = Join-Path $DistDir "lyedu_backend"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

# Dockerfile 已内置国内镜像默认值，直连 Docker Hub 可传: --build-arg DOCKER_REGISTRY= --build-arg PIP_INDEX=
Write-Host "[LyEdu] Building in Docker (Linux target) ..." -ForegroundColor Cyan
$env:DOCKER_BUILDKIT = "1"
$dest = (Resolve-Path $DistDir).Path
$argList = @(
    "build", "-f", "lyedu-api-python/Dockerfile.build",
    "--target", "export", "--progress=plain",
    "--output", "type=local,dest=$dest", "."
)
if ($env:DOCKER_REGISTRY) { $argList += "--build-arg", "DOCKER_REGISTRY=$env:DOCKER_REGISTRY" }
if ($env:PIP_INDEX) { $argList += "--build-arg", "PIP_INDEX=$env:PIP_INDEX" }
Push-Location $RepoRoot
try {
    $ErrorActionPreference = "Continue"
    & docker @argList
    $ErrorActionPreference = "Stop"
} finally {
    Pop-Location
}

if (Test-Path $DistFile) {
    Write-Host "[LyEdu] Build done: lyedu-api-python\dist\lyedu_backend" -ForegroundColor Green
} else {
    Write-Host "[LyEdu] Output not found, check build log above." -ForegroundColor Yellow
    exit 1
}
