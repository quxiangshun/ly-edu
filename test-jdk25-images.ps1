# 测试 JDK 25 镜像可用性

Write-Host "测试 JDK 25 Docker 镜像..." -ForegroundColor Cyan
Write-Host ""

$testImages = @(
    @{Name="Eclipse Temurin JDK 25"; Tag="eclipse-temurin:25-jdk-jammy"},
    @{Name="Eclipse Temurin JRE 25"; Tag="eclipse-temurin:25-jre-jammy"},
    @{Name="Eclipse Temurin JDK 25 (with version)"; Tag="eclipse-temurin:25.0.1-jdk-jammy"},
    @{Name="Maven 3.9 with JDK 25"; Tag="maven:3.9-eclipse-temurin-25"},
    @{Name="Microsoft OpenJDK 25"; Tag="mcr.microsoft.com/openjdk/jdk:25-ubuntu"}
)

$results = @()

foreach ($img in $testImages) {
    Write-Host "测试: $($img.Name)" -ForegroundColor Yellow
    Write-Host "  标签: $($img.Tag)" -ForegroundColor Gray
    
    $startTime = Get-Date
    docker pull $img.Tag 2>&1 | Out-Null
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ 可用 (耗时: $([math]::Round($duration, 2))秒)" -ForegroundColor Green
        $results += @{
            Name = $img.Name
            Tag = $img.Tag
            Available = $true
            Duration = $duration
        }
    } else {
        Write-Host "  ✗ 不可用" -ForegroundColor Red
        $results += @{
            Name = $img.Name
            Tag = $img.Tag
            Available = $false
            Duration = 0
        }
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "测试结果汇总" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$available = $results | Where-Object { $_.Available -eq $true }
$unavailable = $results | Where-Object { $_.Available -eq $false }

if ($available.Count -gt 0) {
    Write-Host "可用镜像 ($($available.Count)):" -ForegroundColor Green
    foreach ($img in $available) {
        Write-Host "  ✓ $($img.Name)" -ForegroundColor Green
        Write-Host "    标签: $($img.Tag)" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($unavailable.Count -gt 0) {
    Write-Host "不可用镜像 ($($unavailable.Count)):" -ForegroundColor Red
    foreach ($img in $unavailable) {
        Write-Host "  ✗ $($img.Name)" -ForegroundColor Red
        Write-Host "    标签: $($img.Tag)" -ForegroundColor Gray
    }
    Write-Host ""
}

# 推荐方案
Write-Host "推荐方案:" -ForegroundColor Cyan
if ($available | Where-Object { $_.Tag -like "*maven*eclipse-temurin-25*" }) {
    Write-Host "  使用标准 Dockerfile (maven:3.9-eclipse-temurin-25)" -ForegroundColor Green
} elseif ($available | Where-Object { $_.Tag -like "*eclipse-temurin:25-jdk*" }) {
    Write-Host "  使用 Dockerfile.manual-maven (手动安装 Maven)" -ForegroundColor Yellow
} elseif ($available | Where-Object { $_.Tag -like "*microsoft*" }) {
    Write-Host "  使用 Dockerfile.alternative (Microsoft OpenJDK)" -ForegroundColor Yellow
} else {
    Write-Host "  使用 Dockerfile.build-jdk25 (手动下载 JDK)" -ForegroundColor Yellow
}

Write-Host ""
