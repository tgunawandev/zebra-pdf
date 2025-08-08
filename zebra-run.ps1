# Zebra Print Control System - Quick Run Script (PowerShell)
# Downloads and runs the pre-built Docker image from Docker Hub

param(
    [switch]$Help
)

# Configuration
$DockerImage = "kodemeio/zebra-pdf:latest"
$ContainerName = "zebra-print-control"

function Write-Banner {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Magenta
    Write-Host "         🦓 ZEBRA PRINT CONTROL SYSTEM        " -ForegroundColor Magenta
    Write-Host "              Quick Run (Docker Hub)          " -ForegroundColor Magenta
    Write-Host "===============================================" -ForegroundColor Magenta
    Write-Host ""
}

function Show-Help {
    Write-Host "This script downloads and runs the Zebra Print Control System" -ForegroundColor Cyan
    Write-Host "from a pre-built Docker image hosted on Docker Hub." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\zebra-run.ps1           - Download and run the system"
    Write-Host "  .\zebra-run.ps1 -Help     - Show this help"
    Write-Host ""
    Write-Host "Requirements:" -ForegroundColor Yellow
    Write-Host "  • Docker Desktop installed and running"
    Write-Host "  • USB Zebra printer connected (optional)"
    Write-Host "  • Ports 5000 and 8631 available"
    Write-Host ""
    exit 0
}

function Test-DockerInstalled {
    try {
        docker --version | Out-Null
        Write-Host "✅ Docker detected" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Docker is not installed or not running" -ForegroundColor Red
        Write-Host "Please install Docker Desktop: https://docs.docker.com/desktop/windows/"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

function Stop-ExistingContainer {
    $existing = docker ps -a --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
    if ($existing -eq $ContainerName) {
        Write-Host "🛑 Stopping existing container..." -ForegroundColor Blue
        docker stop $ContainerName 2>$null | Out-Null
        docker rm $ContainerName 2>$null | Out-Null
    }
}

function Start-ZebraSystem {
    Write-Host "📥 Pulling latest image from Docker Hub..." -ForegroundColor Blue
    docker pull $DockerImage
    
    Write-Host "🚀 Starting Zebra Print Control System..." -ForegroundColor Blue
    
    $dockerArgs = @(
        "run", "-d",
        "--name", $ContainerName,
        "--restart", "unless-stopped",
        "--privileged",
        "-p", "5000:5000",
        "-p", "8631:631",
        "-v", "zebra_data:/app/data",
        "-v", "zebra_logs:/var/log/zebra-print",
        "-e", "ZEBRA_API_HOST=0.0.0.0",
        "-e", "ZEBRA_API_PORT=5000",
        "-e", "ZEBRA_PRINTER_NAME=ZTC-ZD230-203dpi-ZPL",
        "-e", "TZ=UTC",
        $DockerImage
    )
    
    $result = & docker @dockerArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start container" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

function Show-SystemInfo {
    Write-Host ""
    Write-Host "✅ System started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Services available at:" -ForegroundColor Cyan
    Write-Host "  • API Server:    http://localhost:5000"
    Write-Host "  • Health Check:  http://localhost:5000/health"
    Write-Host "  • CUPS Admin:    http://localhost:8631"
    Write-Host ""
    Write-Host "💡 Useful commands:" -ForegroundColor Yellow
    Write-Host "  • Check status:  docker ps"
    Write-Host "  • View logs:     docker logs $ContainerName"
    Write-Host "  • Access shell:  docker exec -it $ContainerName /bin/bash"
    Write-Host "  • Stop system:   docker stop $ContainerName"
    Write-Host ""
    
    # Wait for API to start
    Start-Sleep -Seconds 3
    
    # Quick health check
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -UseBasicParsing
        Write-Host "✅ API is responding" -ForegroundColor Green
    }
    catch {
        Write-Host "⏳ API starting up... (check logs if it doesn't respond in 30s)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Read-Host "Press Enter to exit"
}

# Main execution
Write-Banner

if ($Help) {
    Show-Help
}

Test-DockerInstalled
Stop-ExistingContainer
Start-ZebraSystem
Show-SystemInfo