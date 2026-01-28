# LyEdu Docker 启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LyEdu 企业培训系统 - Docker 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否运行
Write-Host "检查 Docker 状态..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: Docker Desktop 未运行或无法连接！" -ForegroundColor Red
        Write-Host "请先启动 Docker Desktop，然后重试。" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Docker 运行正常" -ForegroundColor Green
} catch {
    Write-Host "错误: 无法连接到 Docker" -ForegroundColor Red
    Write-Host "请确保 Docker Desktop 已启动" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 检查端口占用
Write-Host "检查端口占用..." -ForegroundColor Yellow
$ports = @(3306, 6379, 9700, 9800, 9801, 9900)
$occupiedPorts = @()

foreach ($port in $ports) {
    $result = netstat -ano | Select-String ":$port "
    if ($result) {
        $occupiedPorts += $port
        Write-Host "警告: 端口 $port 已被占用" -ForegroundColor Yellow
    }
}

if ($occupiedPorts.Count -gt 0) {
    Write-Host "以下端口被占用: $($occupiedPorts -join ', ')" -ForegroundColor Yellow
    $continue = Read-Host "是否继续? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

Write-Host ""

# 检查必要文件
Write-Host "检查项目文件..." -ForegroundColor Yellow
$requiredFiles = @(
    "compose.yml",
    "lyedu-api\Dockerfile",
    "lyedu-api\pom.xml",
    "lyedu-admin\Dockerfile",
    "lyedu-pc\Dockerfile",
    "lyedu-h5\Dockerfile",
    "docker\mysql\init.sql"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
        Write-Host "错误: 缺少文件 $file" -ForegroundColor Red
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "缺少必要文件，无法启动" -ForegroundColor Red
    exit 1
}

Write-Host "文件检查通过" -ForegroundColor Green
Write-Host ""

# 启动服务
Write-Host "开始启动服务..." -ForegroundColor Cyan
Write-Host "这可能需要几分钟时间，请耐心等待..." -ForegroundColor Yellow
Write-Host ""

# 先启动数据库
Write-Host "1. 启动 MySQL 和 Redis..." -ForegroundColor Cyan
docker-compose up -d mysql redis

if ($LASTEXITCODE -ne 0) {
    Write-Host "启动数据库失败！" -ForegroundColor Red
    exit 1
}

Write-Host "等待数据库初始化（30秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 启动后端 API
Write-Host "2. 启动后端 API..." -ForegroundColor Cyan
docker-compose up -d --build api

if ($LASTEXITCODE -ne 0) {
    Write-Host "启动 API 失败！查看日志: docker-compose logs api" -ForegroundColor Red
    exit 1
}

Write-Host "等待 API 启动（60秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# 启动前端服务
Write-Host "3. 启动前端服务..." -ForegroundColor Cyan
docker-compose up -d --build admin pc h5

if ($LASTEXITCODE -ne 0) {
    Write-Host "启动前端服务失败！查看日志: docker-compose logs" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "服务启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "  管理后台: http://localhost:9900" -ForegroundColor White
Write-Host "  PC端:     http://localhost:9800" -ForegroundColor White
Write-Host "  H5端:     http://localhost:9801" -ForegroundColor White
Write-Host "  API:      http://localhost:9700/api/hello" -ForegroundColor White
Write-Host ""
Write-Host "查看日志: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "停止服务: docker-compose down" -ForegroundColor Yellow
Write-Host ""
