# LyEdu 开发环境一键启动（根据 dev-config.yml 或 dev-config.json）
# 建议在项目根目录执行: .\scripts\dev\start.ps1
$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$Root = (Resolve-Path (Join-Path (Join-Path $ScriptDir '..') '..')).Path
Set-Location $Root

function Parse-DevConfigValue {
    param([string]$v)
    $v = ($v -replace '\s*#.*$', '').Trim().Trim('"').Trim("'")
    if ($v -eq 'true') { return $true }
    if ($v -eq 'false') { return $false }
    if ($v -match '^\d+$') { return [int]$v }
    return $v
}
function Parse-DevConfigYaml {
    param([string]$path)
    $lines = Get-Content $path -Encoding UTF8
    $config = @{}
    $section = $null
    foreach ($line in $lines) {
        $line = $line -replace '#.*$', ''
        $line = $line.Trim()
        if (-not $line) { continue }
        if ($line -match '^(\w+):\s*$') {
            $section = $matches[1]
            $config[$section] = @{}
            continue
        }
        if ($line -match '^\s{2,}(\w+):\s*(.*)$' -and $section) {
            $config[$section][$matches[1]] = Parse-DevConfigValue $matches[2]
            continue
        }
        if ($line -match '^(\w+):\s*(.*)$' -and -not $line.StartsWith('  ')) {
            $section = $null
            $config[$matches[1]] = Parse-DevConfigValue $matches[2]
            continue
        }
    }
    $db = [PSCustomObject]$config.database
    $redis = [PSCustomObject]$config.redis
    [PSCustomObject]@{
        database = $db
        redis = $redis
        start_docker_mysql_redis = $config['start_docker_mysql_redis']
        start_lyedu_api = $config['start_lyedu_api']
        start_lyedu_api_python = $config['start_lyedu_api_python']
        start_lyedu_admin = $config['start_lyedu_admin']
        start_lyedu_pc = $config['start_lyedu_pc']
    }
}

$ConfigYml = Join-Path $ScriptDir 'dev-config.yml'
$ConfigJson = Join-Path $ScriptDir 'dev-config.json'
if (Test-Path $ConfigYml) {
    $config = Parse-DevConfigYaml $ConfigYml
} elseif (Test-Path $ConfigJson) {
    $config = Get-Content $ConfigJson -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    Write-Host 'Config not found: copy dev-config.example.yml to dev-config.yml and edit.' -ForegroundColor Red
    exit 1
}

$ServersFile = Join-Path $Root '.dev-servers.json'
$servers = @{ windows = @() }

# Optional: start Docker MySQL + Redis
if ($config.start_docker_mysql_redis) {
    $composeFile = Join-Path $Root 'scripts/docker/compose-mysql-redis.yml'
    if (Test-Path $composeFile) {
        Write-Host "Checking Docker MySQL+Redis..." -ForegroundColor Cyan
        $mysqlPort = $config.database.port
        try {
            $conn = Get-NetTCPConnection -LocalPort $mysqlPort -State Listen -ErrorAction SilentlyContinue
        } catch {
            $conn = $null
        }
        if (-not $conn) {
            Write-Host "Starting Docker Compose (MySQL + Redis)..." -ForegroundColor Cyan
            & docker compose -f $composeFile up -d
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Docker start failed. Ensure Docker is installed and running." -ForegroundColor Yellow
            } else {
                Write-Host "Waiting for MySQL..." -ForegroundColor Gray
                Start-Sleep -Seconds 5
            }
        } else {
            Write-Host "MySQL port $mysqlPort already in use, skipping Docker." -ForegroundColor Gray
        }
    }
}

function Start-InNewWindow {
    param([string]$Title, [string]$Command, [string]$WorkDir = $Root)
    $arg = '-NoExit', '-Command', $Command
    $proc = Start-Process powershell -ArgumentList $arg -WorkingDirectory $WorkDir -PassThru
    $servers.windows += @{ name = $Title; pid = $proc.Id }
    Write-Host ('Started: ' + $Title + ' (PID ' + $proc.Id + ')') -ForegroundColor Green
}

# Python API
if ($config.start_lyedu_api_python) {
    $apiPyDir = Join-Path $Root 'lyedu-api-python'
    if (-not (Test-Path $apiPyDir)) {
        Write-Host 'Skip lyedu-api-python: dir not found' -ForegroundColor Yellow
    } else {
        $venvPath = Join-Path $apiPyDir '.venv'
        if (-not (Test-Path $venvPath)) {
            Write-Host 'Init lyedu-api-python venv...' -ForegroundColor Cyan
            Push-Location $apiPyDir
            & python -m venv .venv
            & .\.venv\Scripts\Activate.ps1
            & pip install -r requirements.txt -q
            Pop-Location
        } else {
            Push-Location $apiPyDir
            $pipExe = Join-Path $apiPyDir '.venv\Scripts\pip.exe'
            $pythonExe = Join-Path $apiPyDir '.venv\Scripts\python.exe'
            $reqFile = Join-Path $apiPyDir 'requirements.txt'
            $needInstall = $false
            if (Test-Path $pythonExe) {
                $errFile = [System.IO.Path]::GetTempFileName()
                $outFile = [System.IO.Path]::GetTempFileName()
                try {
                    $p = Start-Process -FilePath $pythonExe -ArgumentList '-c', 'import openpyxl' -Wait -NoNewWindow -PassThru -RedirectStandardError $errFile -RedirectStandardOutput $outFile
                    if ($p.ExitCode -ne 0) { $needInstall = $true }
                } finally {
                    Remove-Item $errFile -Force -ErrorAction SilentlyContinue
                    Remove-Item $outFile -Force -ErrorAction SilentlyContinue
                }
            } else {
                $needInstall = $true
            }
            if ($needInstall -and (Test-Path $reqFile)) {
                Write-Host 'Install lyedu-api-python deps (e.g. openpyxl)...' -ForegroundColor Cyan
                & $pipExe install -r requirements.txt -q
            }
            Pop-Location
        }
        $db = $config.database
        $redis = $config.redis
        $runnerPath = Join-Path $apiPyDir '_start_runner.ps1'
        $runnerContent = @"
`$env:PYTHONUTF8 = '1'
`$env:ENV = 'dev'
`$env:HOST = '0.0.0.0'
`$env:PORT = '9700'
`$env:MYSQL_HOST = '$($db.host)'
`$env:MYSQL_PORT = '$($db.port)'
`$env:MYSQL_USERNAME = '$($db.user)'
`$env:MYSQL_PASSWORD = '$($db.password)'
`$env:MYSQL_DATABASE = '$($db.database)'
`$env:REDIS_HOST = '$($redis.host)'
`$env:REDIS_PORT = '$($redis.port)'
.\.venv\Scripts\Activate.ps1
Write-Host 'Running Alembic...' -ForegroundColor Cyan
& alembic upgrade head
if (`$LASTEXITCODE -ne 0) { Write-Host 'Alembic failed, starting anyway...' -ForegroundColor Yellow }
Write-Host 'Starting uvicorn :9700' -ForegroundColor Green
& uvicorn main:app --reload --host 0.0.0.0 --port 9700
"@
        Set-Content -Path $runnerPath -Value $runnerContent -Encoding UTF8
        $sq = [char]39
        $amp = [char]38
        $sp = [char]32
        $sqStr = $sq.ToString()
        $cmd = $amp.ToString() + $sp + $sq + $runnerPath.Replace($sqStr, $sqStr + $sqStr) + $sq
        Start-InNewWindow -Title 'lyedu-api-python' -Command $cmd -WorkDir $apiPyDir
    }
}

# 管理后台
if ($config.start_lyedu_admin) {
    $adminDir = Join-Path $Root 'lyedu-admin'
    if (-not (Test-Path $adminDir)) {
        Write-Host 'Skip lyedu-admin: dir not found' -ForegroundColor Yellow
    } else {
        $nm = Join-Path $adminDir 'node_modules'
        if (-not (Test-Path $nm)) {
            Write-Host 'Init lyedu-admin (npm install)...' -ForegroundColor Cyan
            Push-Location $adminDir
            & npm install
            Pop-Location
        }
        $cmd = 'npm run dev'
        Start-InNewWindow -Title 'lyedu-admin' -Command $cmd -WorkDir $adminDir
    }
}

# PC 端
if ($config.start_lyedu_pc) {
    $pcDir = Join-Path $Root 'lyedu-pc'
    if (-not (Test-Path $pcDir)) {
        Write-Host 'Skip lyedu-pc: dir not found' -ForegroundColor Yellow
    } else {
        $nm = Join-Path $pcDir 'node_modules'
        if (-not (Test-Path $nm)) {
            Write-Host 'Init lyedu-pc (npm install)...' -ForegroundColor Cyan
            Push-Location $pcDir
            & npm install
            Pop-Location
        }
        $cmd = 'npm run dev'
        Start-InNewWindow -Title 'lyedu-pc' -Command $cmd -WorkDir $pcDir
    }
}

# Java API（可选）
if ($config.start_lyedu_api) {
    $apiDir = Join-Path $Root 'lyedu-api'
    if (-not (Test-Path $apiDir)) {
        Write-Host 'Skip lyedu-api: dir not found' -ForegroundColor Yellow
    } else {
        $gradlew = Join-Path $apiDir 'gradlew.bat'
        if (-not (Test-Path $gradlew)) { $gradlew = Join-Path $apiDir 'gradlew' }
        $sq = [char]39
        $amp = [char]38
        $sp = [char]32
        $sqStr = $sq.ToString()
        $gradlewEsc = $gradlew.Replace($sqStr, $sqStr + $sqStr)
        $cmd = $amp.ToString() + $sp + $sq + $gradlewEsc + $sq + $sp + 'bootRun'
        Start-InNewWindow -Title 'lyedu-api' -Command $cmd -WorkDir $apiDir
    }
}

# 保存 PID 列表供 stop.ps1 使用（写在仓库根目录）
$servers | ConvertTo-Json -Depth 5 | Set-Content $ServersFile -Encoding UTF8
Write-Host ""
Write-Host 'Dev env started. Stop: .\scripts\dev\stop.ps1' -ForegroundColor Cyan
