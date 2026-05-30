# Inicia todos los microservicios CrediActiva + API Gateway
$ErrorActionPreference = "Stop"
$BackendRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $BackendRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Creando entorno virtual..."
    py -3 -m venv (Join-Path $BackendRoot ".venv")
    & (Join-Path $BackendRoot ".venv\Scripts\pip.exe") install -r (Join-Path $BackendRoot "services\requirements.txt")
}

$services = @(
    @{ Name = "auth-service";   Dir = "services\auth_service";   Port = 8001 },
    @{ Name = "credit-service"; Dir = "services\credit_service"; Port = 8002 },
    @{ Name = "payment-service"; Dir = "services\payment_service"; Port = 8003 },
    @{ Name = "portal-service"; Dir = "services\portal_service"; Port = 8004 },
    @{ Name = "api-gateway";    Dir = "gateway";                 Port = 8000 }
)

Write-Host "`n=== CrediActiva Microservicios ===" -ForegroundColor Cyan
foreach ($svc in $services) {
    $workDir = Join-Path $BackendRoot $svc.Dir
    Write-Host "Iniciando $($svc.Name) en puerto $($svc.Port)..." -ForegroundColor Green
    Start-Process -FilePath $Python `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$($svc.Port)" `
        -WorkingDirectory $workDir `
        -WindowStyle Minimized
    Start-Sleep -Milliseconds 800
}

Write-Host "`nTodos los servicios iniciados." -ForegroundColor Cyan
Write-Host "API Gateway:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Docs Gateway: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend:     http://localhost:4200" -ForegroundColor Yellow
Write-Host "`nHealth check: http://localhost:8000/health`n"
