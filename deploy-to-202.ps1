param(
    [string]$Server = "war12oc@192.168.2.202",
    [string]$HosxpHost = "192.168.2.254",
    [string]$HosxpUser = "opd",
    [string]$HosxpPassword = "opd",
    [string]$HosxpDatabase = "hos"
)

$ErrorActionPreference = 'Stop'
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectPath

$archive = Join-Path $env:TEMP 'kspconnect-deploy.tar.gz'
$envFile = Join-Path $env:TEMP 'kspconnect.env'

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Deploying KSP Connect to $Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Build Deployment Archive
Write-Host "[1/3] Building deployment archive..." -ForegroundColor Yellow
if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive -Force }

& tar.exe -czf $archive `
    --exclude='./venv' `
    --exclude='./.venv' `
    --exclude='./__pycache__' `
    --exclude='./.git' `
    --exclude='./.env' `
    .
if ($LASTEXITCODE -ne 0) { throw "Failed to build archive" }

# 2. Generate temporary .env file
$envContent = @"
HOS_DB_HOST=$HosxpHost
HOS_DB_PORT=3306
HOS_DB_USER=$HosxpUser
HOS_DB_PASSWORD=$HosxpPassword
HOS_DB_NAME=$HosxpDatabase
HOS_DB_TIMEOUT=10
HOSPITAL_NAME=โรงพยาบาลเกษตรสมบูรณ์ (KSP)
HOSPITAL_CODE=10714
HOSPITAL_BED_CAPACITY=90
ENABLE_PDPA_MASKING=true
REST_HOST=0.0.0.0
REST_PORT=8000
"@
[IO.File]::WriteAllText($envFile, $envContent, [Text.Encoding]::UTF8)

try {
    # 3. Upload files to 192.168.2.202
    Write-Host "[2/3] Uploading archive to ${Server}:/tmp/ (Enter SSH password if prompted)..." -ForegroundColor Yellow
    $installScript = Join-Path $projectPath "remote-install.sh"
    & scp.exe $archive $envFile $installScript "${Server}:/tmp/"
    if ($LASTEXITCODE -ne 0) { throw "SCP upload failed." }

    # 4. Execute remote installation script
    Write-Host "[3/3] Running remote installer on server (Enter sudo password if prompted)..." -ForegroundColor Yellow
    & ssh.exe -tt $Server "bash /tmp/remote-install.sh"
    if ($LASTEXITCODE -ne 0) { throw "Remote installation failed." }

    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "🎉 Deployment to 192.168.2.202 completed successfully!" -ForegroundColor Green
    Write-Host "👉 Test endpoint: http://192.168.2.202:8000/api/v1/overview" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive -Force }
    if (Test-Path -LiteralPath $envFile) { Remove-Item -LiteralPath $envFile -Force }
}
