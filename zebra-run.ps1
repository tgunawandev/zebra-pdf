# Zebra Print Control System - Enhanced Quick Run Script (PowerShell)
# Downloads and runs the pre-built Docker image from Docker Hub
# with support for environment variables, .env files, and interactive setup

param(
    [switch]$Setup,
    [string]$EnvFile = "",
    [string]$Domain = "",
    [string]$Tunnel = "",
    [switch]$Help
)

# Configuration
$DockerImage = "kodemeio/zebra-pdf:latest"
$ContainerName = "zebra-print-control"
$DefaultEnvFile = ".env"

function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║          ZEBRA PRINT CONTROL SYSTEM          ║" -ForegroundColor Magenta
    Write-Host "║              Quick Run (Docker Hub)          ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

function Show-Help {
    Write-Banner
    Write-Host "This script downloads and runs the Zebra Print Control System" -ForegroundColor Cyan
    Write-Host "from a pre-built Docker image hosted on Docker Hub." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\zebra-run.ps1                          - Download and run the system"
    Write-Host "  .\zebra-run.ps1 -Setup                   - Run with interactive setup after start"
    Write-Host "  .\zebra-run.ps1 -EnvFile [file]          - Use custom environment file"
    Write-Host "  .\zebra-run.ps1 -Domain [domain]         - Set tunnel domain directly"
    Write-Host "  .\zebra-run.ps1 -Tunnel [type]           - Set tunnel type (cloudflare/ngrok)"
    Write-Host "  .\zebra-run.ps1 -Help                    - Show this help"
    Write-Host ""
    Write-Host "Environment Variables:" -ForegroundColor Yellow
    Write-Host "  ZEBRA_DOMAIN                - Custom domain for tunnel"
    Write-Host "  ZEBRA_TUNNEL_TYPE           - Tunnel type (cloudflare/ngrok)"
    Write-Host "  CLOUDFLARE_TOKEN            - Cloudflare tunnel token"
    Write-Host "  NGROK_AUTHTOKEN             - Ngrok authentication token"
    Write-Host "  ZEBRA_PRINTER_NAME          - Custom printer name"
    Write-Host ""
    Write-Host ".env File Example:" -ForegroundColor Yellow
    Write-Host "  ZEBRA_DOMAIN=tln-zebra-01.abcfood.app"
    Write-Host "  ZEBRA_TUNNEL_TYPE=cloudflare"
    Write-Host "  CLOUDFLARE_TOKEN=your_token_here"
    Write-Host ""
    Write-Host "Requirements:" -ForegroundColor Yellow
    Write-Host "  • Docker Desktop installed and running"
    Write-Host "  • USB Zebra printer connected (optional)"
    Write-Host "  • Ports 5000 and 8631 available"
    Write-Host ""
    exit 0
}

function Load-EnvFile {
    $envPath = if ($EnvFile) { $EnvFile } else { $DefaultEnvFile }
    
    if (Test-Path $envPath) {
        Write-Host "[LOAD] Loading environment from: $envPath" -ForegroundColor Blue
        
        Get-Content $envPath | ForEach-Object {
            $line = $_.Trim()
            # Skip comments and empty lines
            if ($line -match "^#" -or $line -eq "") { return }
            
            # Only process ZEBRA_, CLOUDFLARE_, and NGROK_ variables
            if ($line -match "^(ZEBRA_|CLOUDFLARE_|NGROK_)") {
                $parts = $line.Split('=', 2)
                if ($parts.Length -eq 2) {
                    $varName = $parts[0]
                    $varValue = $parts[1]
                    [Environment]::SetEnvironmentVariable($varName, $varValue, "Process")
                    Write-Host "  ✓ $line" -ForegroundColor Cyan
                }
            }
        }
    } elseif ($EnvFile) {
        Write-Host "WARNING: Environment file not found: $envPath" -ForegroundColor Yellow
    }
}

function Test-DockerInstalled {
    try {
        docker --version | Out-Null
        Write-Host "[OK] Docker detected" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[ERROR] Docker is not installed or not running" -ForegroundColor Red
        Write-Host "Please install Docker Desktop: https://docs.docker.com/desktop/windows/"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

function Stop-ExistingContainer {
    $existing = docker ps -a --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
    if ($existing -eq $ContainerName) {
        Write-Host "[STOP] Stopping existing container..." -ForegroundColor Blue
        docker stop $ContainerName 2>$null | Out-Null
        docker rm $ContainerName 2>$null | Out-Null
    }
}

function Build-DockerEnvArgs {
    $envArgs = @()
    
    # Base environment variables
    $envArgs += "-e", "ZEBRA_API_HOST=0.0.0.0"
    $envArgs += "-e", "ZEBRA_API_PORT=5000"
    $envArgs += "-e", "TZ=UTC"
    
    # Custom printer name
    $printerName = $env:ZEBRA_PRINTER_NAME
    if (-not $printerName) { $printerName = "ZTC-ZD230-203dpi-ZPL" }
    $envArgs += "-e", "ZEBRA_PRINTER_NAME=$printerName"
    
    # Tunnel configuration
    $domainValue = if ($Domain) { $Domain } else { $env:ZEBRA_DOMAIN }
    if ($domainValue) {
        $envArgs += "-e", "ZEBRA_DOMAIN=$domainValue"
    }
    
    $tunnelValue = if ($Tunnel) { $Tunnel } else { $env:ZEBRA_TUNNEL_TYPE }
    if ($tunnelValue) {
        $envArgs += "-e", "ZEBRA_TUNNEL_TYPE=$tunnelValue"
    }
    
    # Cloudflare token
    if ($env:CLOUDFLARE_TOKEN) {
        $envArgs += "-e", "CLOUDFLARE_TOKEN=$($env:CLOUDFLARE_TOKEN)"
    }
    
    # Ngrok token
    if ($env:NGROK_AUTHTOKEN) {
        $envArgs += "-e", "NGROK_AUTHTOKEN=$($env:NGROK_AUTHTOKEN)"
    }
    
    return $envArgs
}

function Start-ZebraSystem {
    Write-Host "[PULL] Pulling latest image from Docker Hub..." -ForegroundColor Blue
    docker pull $DockerImage
    
    Write-Host "[START] Starting Zebra Print Control System..." -ForegroundColor Blue
    
    # Build environment arguments
    $envArgs = Build-DockerEnvArgs
    
    # Show configuration if any tunnel settings are present
    $domainValue = if ($Domain) { $Domain } else { $env:ZEBRA_DOMAIN }
    $tunnelValue = if ($Tunnel) { $Tunnel } else { $env:ZEBRA_TUNNEL_TYPE }
    
    if ($domainValue -or $tunnelValue) {
        Write-Host "[CONFIG] Configuration:" -ForegroundColor Cyan
        if ($domainValue) { Write-Host "  • Domain: $domainValue" }
        if ($tunnelValue) { Write-Host "  • Tunnel: $tunnelValue" }
    }
    
    # Create network if it doesn't exist
    $networkExists = docker network ls --filter "name=zebra-print-network" --format "{{.Name}}" 2>$null
    if ($networkExists -ne "zebra-print-network") {
        Write-Host "[NETWORK] Creating zebra-print-network..." -ForegroundColor Blue
        docker network create zebra-print-network | Out-Null
    }
    
    # Build full Docker arguments
    $dockerArgs = @(
        "run", "-d",
        "--name", $ContainerName,
        "--restart", "unless-stopped",
        "--privileged",
        "--pull", "always",
        "--network", "zebra-print-network",
        "-p", "5000:5000",
        "-p", "8631:631",
        "-v", "zebra_data:/app/data",
        "-v", "zebra_logs:/var/log/zebra-print"
    )
    
    # Add environment arguments
    $dockerArgs += $envArgs
    
    # Add image name
    $dockerArgs += $DockerImage
    
    # Run container
    $result = & docker @dockerArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to start container" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

function Start-Tunnel {
    $domainValue = if ($Domain) { $Domain } else { $env:ZEBRA_DOMAIN }
    $tunnelValue = if ($Tunnel) { $Tunnel } else { $env:ZEBRA_TUNNEL_TYPE }
    
    if (-not $domainValue -or -not $tunnelValue) {
        return $false  # No tunnel configuration
    }
    
    Write-Host "[TUNNEL] Starting $tunnelValue tunnel for $domainValue..." -ForegroundColor Blue
    
    if ($tunnelValue -eq "cloudflare" -and $env:CLOUDFLARE_TOKEN) {
        # Start Cloudflare tunnel
        docker exec -d $ContainerName bash -c "cloudflared tunnel --url http://127.0.0.1:5000 run --token $($env:CLOUDFLARE_TOKEN) > /var/log/cloudflare.log 2>&1"
        
        # Wait for tunnel to establish
        Write-Host "[WAIT] Establishing tunnel connections..." -ForegroundColor Yellow
        Start-Sleep -Seconds 8
        
        # Check if tunnel process is running
        $tunnelRunning = docker exec $ContainerName bash -c "ps aux | grep -q '[c]loudflared'; echo `$?"
        if ($tunnelRunning -eq "0") {
            Write-Host "[OK] Cloudflare tunnel started" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[ERROR] Cloudflare tunnel failed to start" -ForegroundColor Red
            return $false
        }
        
    } elseif ($tunnelValue -eq "ngrok" -and $env:NGROK_AUTHTOKEN) {
        # Start Ngrok tunnel
        docker exec -d $ContainerName bash -c "ngrok http 5000 --authtoken=$($env:NGROK_AUTHTOKEN) > /var/log/ngrok.log 2>&1"
        
        Write-Host "[WAIT] Starting ngrok tunnel..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        $tunnelRunning = docker exec $ContainerName bash -c "ps aux | grep -q '[n]grok'; echo `$?"
        if ($tunnelRunning -eq "0") {
            Write-Host "[OK] Ngrok tunnel started" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[ERROR] Ngrok tunnel failed to start" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "[WARNING] Tunnel configuration incomplete" -ForegroundColor Yellow
        Write-Host "  • Type: $tunnelValue"
        $tokenPresent = if ($env:CLOUDFLARE_TOKEN -or $env:NGROK_AUTHTOKEN) { "Present" } else { "Missing" }
        Write-Host "  • Token: $tokenPresent"
        return $false
    }
}

function Test-Tunnel {
    $domainValue = if ($Domain) { $Domain } else { $env:ZEBRA_DOMAIN }
    
    if (-not $domainValue) {
        return $true  # No tunnel to verify
    }
    
    Write-Host "[CHECK] Verifying tunnel connectivity..." -ForegroundColor Blue
    
    # Try to reach the health endpoint
    $maxAttempts = 3
    
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri "https://$domainValue/health" -TimeoutSec 10 -UseBasicParsing
            Write-Host "[OK] Tunnel is working: https://$domainValue" -ForegroundColor Green
            Write-Host "[INFO] Webhook URL: https://$domainValue/print" -ForegroundColor Cyan
            return $true
        }
        catch {
            Write-Host "[WAIT] Attempt $attempt/$maxAttempts..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
    
    Write-Host "[ERROR] Tunnel verification failed" -ForegroundColor Red
    Write-Host "   Common fixes:" -ForegroundColor Yellow
    Write-Host "  1. Check Cloudflare dashboard tunnel configuration"
    Write-Host "  2. Ensure domain points to: http://localhost:5000"
    Write-Host "  3. Verify tunnel token is correct"
    Write-Host "  4. Check logs: docker logs $ContainerName"
    return $false
}

function Show-SystemInfo {
    Write-Host "[OK] System started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[INFO] Services available at:" -ForegroundColor Cyan
    Write-Host "  • API Server:    http://localhost:5000"
    Write-Host "  • Health Check:  http://localhost:5000/health"
    Write-Host "  • CUPS Admin:    http://localhost:8631"
    Write-Host ""
    
    # Wait for container to start
    Start-Sleep -Seconds 3
    
    # Quick health check
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -UseBasicParsing
        Write-Host "[OK] Local API is responding" -ForegroundColor Green
    }
    catch {
        Write-Host "[WAIT] API starting up... (check logs if it doesn't respond in 30s)" -ForegroundColor Yellow
        return $false
    }
    
    # Auto-start and verify tunnel if configured
    $domainValue = if ($Domain) { $Domain } else { $env:ZEBRA_DOMAIN }
    if ($domainValue) {
        Write-Host ""
        if ((Start-Tunnel) -and (Test-Tunnel)) {
            Write-Host ""
            Write-Host "✓ System fully operational!" -ForegroundColor Green
            Write-Host "-> Tunnel Access: https://$domainValue" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "[WARNING] Local system working, tunnel needs attention" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "   Useful commands:" -ForegroundColor Yellow
    Write-Host "  • Check status:  docker ps"
    Write-Host "  • View logs:     docker logs $ContainerName"
    Write-Host "  • Access shell:  docker exec -it $ContainerName /bin/bash"
    Write-Host "  • Stop system:   docker stop $ContainerName"
}

function Start-InteractiveSetup {
    Write-Host ">> Starting interactive setup..." -ForegroundColor Blue
    Write-Host "   Accessing container control panel..." -ForegroundColor Yellow
    
    # Wait a moment for container to be ready
    Start-Sleep -Seconds 3
    
    # Run the interactive setup
    docker exec -it $ContainerName python3 zebra_control_v2.py
}

function New-SampleEnvFile {
    if (-not (Test-Path $DefaultEnvFile)) {
        Write-Host "[CREATE] Creating sample .env file..." -ForegroundColor Blue
        
        $envContent = @"
# Zebra Print Control System Configuration
# Uncomment and configure the variables you need

# Tunnel Configuration
# ZEBRA_DOMAIN=tln-zebra-01.abcfood.app
# ZEBRA_TUNNEL_TYPE=cloudflare

# Cloudflare Tunnel (if using cloudflare)
# CLOUDFLARE_TOKEN=your_cloudflare_tunnel_token_here

# Ngrok Tunnel (if using ngrok)
# NGROK_AUTHTOKEN=your_ngrok_auth_token_here

# Printer Configuration
# ZEBRA_PRINTER_NAME=ZTC-ZD230-203dpi-ZPL
"@
        
        Set-Content -Path $DefaultEnvFile -Value $envContent -Encoding UTF8
        Write-Host "[OK] Sample .env file created. Edit it with your configuration." -ForegroundColor Green
    }
}

# Main execution
Write-Banner

if ($Help) {
    Show-Help
}

Load-EnvFile
Test-DockerInstalled
Stop-ExistingContainer
Start-ZebraSystem
Show-SystemInfo

# Create sample .env if it doesn't exist
New-SampleEnvFile

# Run interactive setup if requested
if ($Setup) {
    Start-InteractiveSetup
}

Write-Host ""
Read-Host "Press Enter to exit"