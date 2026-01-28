# JDK 25 Docker 镜像修复脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "JDK 25 Docker 镜像修复工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否运行
Write-Host "检查 Docker 状态..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: Docker Desktop 未运行！" -ForegroundColor Red
        exit 1
    }
    Write-Host "Docker 运行正常" -ForegroundColor Green
} catch {
    Write-Host "错误: Docker Desktop 未运行！" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 测试镜像下载
Write-Host "测试 JDK 25 镜像下载..." -ForegroundColor Yellow

$images = @(
    "eclipse-temurin:25-jdk-jammy",
    "eclipse-temurin:25-jre-jammy",
    "maven:3.9-eclipse-temurin-25",
    "mcr.microsoft.com/openjdk/jdk:25-ubuntu"
)

$availableImages = @()

foreach ($image in $images) {
    Write-Host "测试镜像: $image" -ForegroundColor Cyan
    docker pull $image 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ 可用" -ForegroundColor Green
        $availableImages += $image
    } else {
        Write-Host "  ✗ 不可用" -ForegroundColor Red
    }
}

Write-Host ""

if ($availableImages.Count -eq 0) {
    Write-Host "所有镜像都不可用，可能是网络问题" -ForegroundColor Red
    Write-Host ""
    Write-Host "建议解决方案：" -ForegroundColor Yellow
    Write-Host "1. 配置 Docker 镜像加速器（见 JDK25_DOCKER_FIX.md）" -ForegroundColor White
    Write-Host "2. 检查网络连接" -ForegroundColor White
    Write-Host "3. 使用代理（如果需要）" -ForegroundColor White
    Write-Host ""
    
    $useAlternative = Read-Host "是否使用备选 Dockerfile (Dockerfile.build-jdk25)? (y/n)"
    if ($useAlternative -eq "y" -or $useAlternative -eq "Y") {
        Write-Host "修改 compose.yml 使用备选 Dockerfile..." -ForegroundColor Yellow
        # 这里可以自动修改 compose.yml
        Write-Host "请手动修改 compose.yml 中的 dockerfile 为: Dockerfile.build-jdk25" -ForegroundColor Yellow
    }
    exit 1
}

Write-Host "找到 $($availableImages.Count) 个可用镜像" -ForegroundColor Green
Write-Host ""

# 根据可用镜像选择最佳方案
if ($availableImages -contains "maven:3.9-eclipse-temurin-25" -and $availableImages -contains "eclipse-temurin:25-jre-jammy") {
    Write-Host "使用标准镜像方案（推荐）" -ForegroundColor Green
    Write-Host "当前 Dockerfile 应该可以正常工作" -ForegroundColor Green
} elseif ($availableImages -contains "mcr.microsoft.com/openjdk/jdk:25-ubuntu") {
    Write-Host "使用 Microsoft OpenJDK 25 方案" -ForegroundColor Yellow
    Write-Host "建议使用 Dockerfile.alternative" -ForegroundColor Yellow
    
    $switch = Read-Host "是否切换到备选 Dockerfile? (y/n)"
    if ($switch -eq "y" -or $switch -eq "Y") {
        # 备份原 Dockerfile
        if (Test-Path "lyedu-api\Dockerfile") {
            Copy-Item "lyedu-api\Dockerfile" "lyedu-api\Dockerfile.backup"
            Write-Host "已备份原 Dockerfile" -ForegroundColor Green
        }
        
        # 使用备选方案
        Copy-Item "lyedu-api\Dockerfile.alternative" "lyedu-api\Dockerfile"
        Write-Host "已切换到备选 Dockerfile" -ForegroundColor Green
    }
} else {
    Write-Host "使用手动构建方案" -ForegroundColor Yellow
    Write-Host "建议使用 Dockerfile.build-jdk25" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "现在可以尝试构建：" -ForegroundColor Cyan
Write-Host "  docker-compose build api" -ForegroundColor White
Write-Host ""
