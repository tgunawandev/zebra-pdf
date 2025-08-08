# Zebra Print Control System - PowerShell Management Script
# Advanced Windows management with PowerShell features

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [string]$Domain,
    [switch]$Force
)

# Configuration
$ContainerName = "zebra-print-control"
$BaseUrl = "http://localhost:5000"

# Colors for PowerShell
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    Magenta = "Magenta"
}

function Write-Banner {
    Write-Host "`n╔══════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║         🦓 ZEBRA PRINT CONTROL SYSTEM        ║" -ForegroundColor Magenta
    Write-Host "║           PowerShell Management CLI          ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════╝`n" -ForegroundColor Magenta
}

function Write-Help {
    Write-Banner
    Write-Host "Usage: .\zebra.ps1 <command> [options]`n" -ForegroundColor Cyan
    
    Write-Host "🚀 Container Management:" -ForegroundColor Yellow
    Write-Host "  start     - Build and start the system"
    Write-Host "  stop      - Stop the system"
    Write-Host "  restart   - Restart the system"
    Write-Host "  status    - Show detailed system status"
    Write-Host "  logs      - Show container logs (interactive)"
    Write-Host "  shell     - Access container shell"
    Write-Host ""
    
    Write-Host "🔧 Configuration:" -ForegroundColor Yellow
    Write-Host "  setup     - Interactive setup wizard"
    Write-Host "  domain    - Configure custom domain (use -Domain parameter)"
    Write-Host "  tunnel    - Manage tunnel configuration"
    Write-Host ""
    
    Write-Host "🧪 Testing & Maintenance:" -ForegroundColor Yellow
    Write-Host "  test      - Run comprehensive system tests"
    Write-Host "  clean     - Clean up containers and images (use -Force to skip prompt)"
    Write-Host "  backup    - Backup configuration to timestamped file"
    Write-Host "  restore   - Restore configuration from backup"
    Write-Host ""
    
    Write-Host "📊 Monitoring:" -ForegroundColor Yellow
    Write-Host "  health    - Comprehensive health check"
    Write-Host "  printer   - Detailed printer status and diagnostics"
    Write-Host "  api       - Test all API endpoints"
    Write-Host "  monitor   - Real-time monitoring dashboard"
    Write-Host ""
    
    Write-Host "🛠️ Windows-Specific:" -ForegroundColor Yellow
    Write-Host "  service   - Install/manage as Windows service"
    Write-Host "  firewall  - Configure Windows Firewall rules"
    Write-Host "  desktop   - Create desktop shortcuts"
    Write-Host ""
    
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\zebra.ps1 start"
    Write-Host "  .\zebra.ps1 domain -Domain 'tln-zebra-01.abcfood.app'"
    Write-Host "  .\zebra.ps1 clean -Force"
    Write-Host ""
}

function Test-Requirements {
    $errors = @()
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        $errors += "Docker is not installed or not in PATH"
    }
    
    if (-not (docker compose version 2>$null)) {
        $errors += "Docker Compose is not available"
    }
    
    if ($errors.Count -gt 0) {
        Write-Host "❌ Requirements check failed:" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "   • $_" -ForegroundColor Red }
        Write-Host "`n💡 Please install Docker Desktop: https://docs.docker.com/desktop/windows/" -ForegroundColor Yellow
        exit 1
    }
}

function Start-System {
    Write-Host "🚀 Starting Zebra Print Control System..." -ForegroundColor Blue
    
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Host "❌ docker-compose.yml not found" -ForegroundColor Red
        exit 1
    }
    
    # Check for USB devices (Windows approach)
    try {
        $usbDevices = Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.Name -like "*Zebra*" }
        if ($usbDevices) {
            Write-Host "✅ Zebra device(s) detected:" -ForegroundColor Green
            $usbDevices | ForEach-Object { Write-Host "   • $($_.Name)" -ForegroundColor Green }
        } else {
            Write-Host "⚠️ No Zebra devices detected on host" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ℹ️ Could not check USB devices" -ForegroundColor Blue
    }
    
    # Start system
    $result = docker compose up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ System started successfully!" -ForegroundColor Green
        Write-Host "`n🌐 Services available at:" -ForegroundColor Cyan
        Write-Host "  • API Server:    $BaseUrl"
        Write-Host "  • Health Check:  $BaseUrl/health"
        Write-Host "  • CUPS Admin:    http://localhost:8631"
        Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
        Write-Host "  • Run: .\zebra.ps1 setup    (for initial configuration)"
        Write-Host "  • Run: .\zebra.ps1 status   (to check system status)"
        Write-Host "  • Run: .\zebra.ps1 shell    (to access control panel)"
    } else {
        Write-Host "❌ Failed to start system" -ForegroundColor Red
        exit 1
    }
}

function Stop-System {
    Write-Host "🛑 Stopping Zebra Print Control System..." -ForegroundColor Blue
    docker compose down
    Write-Host "✅ System stopped" -ForegroundColor Green
}

function Show-Status {
    Write-Host "📊 System Status:" -ForegroundColor Blue
    Write-Host ("-" * 50) -ForegroundColor Blue
    
    # Container status
    $containerInfo = docker ps --filter name=$ContainerName --format "{{.Names}}`t{{.Status}}`t{{.Ports}}" | Select-String $ContainerName
    if ($containerInfo) {
        Write-Host "✅ Container: Running" -ForegroundColor Green
        Write-Host "   Status: $($containerInfo -split "`t" | Select-Object -Skip 1 -First 1)"
        Write-Host "   Ports: $($containerInfo -split "`t" | Select-Object -Skip 2 -First 1)"
        
        # API Health
        try {
            $response = Invoke-WebRequest -Uri "$BaseUrl/health" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ API: Healthy" -ForegroundColor Green
                $healthData = $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
                if ($healthData) {
                    Write-Host "   Printer: $($healthData.printer)"
                    Write-Host "   Timestamp: $($healthData.timestamp)"
                }
            }
        } catch {
            Write-Host "❌ API: Not responding" -ForegroundColor Red
        }
        
        # Container stats
        Write-Host "`n📈 Resource Usage:" -ForegroundColor Cyan
        $stats = docker stats --no-stream --format "{{.CPUPerc}}`t{{.MemUsage}}`t{{.NetIO}}" $ContainerName 2>$null
        if ($stats) {
            $statsParts = $stats -split "`t"
            Write-Host "   CPU: $($statsParts[0])"
            Write-Host "   Memory: $($statsParts[1])"
            Write-Host "   Network: $($statsParts[2])"
        }
    } else {
        Write-Host "❌ Container: Not running" -ForegroundColor Red
    }
    
    # Data volumes
    Write-Host "`n🗄️ Data Volumes:" -ForegroundColor Cyan
    $volumes = docker volume ls --filter name=zebra --format "{{.Name}}`t{{.Driver}}"
    if ($volumes) {
        $volumes | ForEach-Object {
            $parts = $_ -split "`t"
            Write-Host "   • $($parts[0]) ($($parts[1]))"
        }
    } else {
        Write-Host "   No volumes found"
    }
}

function Set-CustomDomain {
    param([string]$DomainName)
    
    if (-not $DomainName) {
        $DomainName = Read-Host "Enter your custom domain (e.g., tln-zebra-01.abcfood.app)"
    }
    
    if ([string]::IsNullOrWhiteSpace($DomainName)) {
        Write-Host "❌ Domain cannot be empty" -ForegroundColor Red
        return
    }
    
    # Validate domain format
    if ($DomainName -notmatch '^[a-z0-9.-]+\.[a-z]{2,}$') {
        Write-Host "❌ Invalid domain format" -ForegroundColor Red
        return
    }
    
    Write-Host "🔧 Configuring domain: $DomainName" -ForegroundColor Blue
    
    $script = @"
from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
tunnel = CloudflareNamedTunnel()
success, message = tunnel.set_custom_domain('$DomainName')
print('✅ ' + message if success else '❌ ' + message)
if success:
    print('🔗 Webhook URL: https://$DomainName/print')
    print('💡 Next: Run authentication with: cloudflared tunnel login')
"@
    
    docker exec -it $ContainerName python3 -c $script
}

function Test-SystemHealth {
    Write-Host "🏥 Comprehensive Health Check" -ForegroundColor Blue
    Write-Host ("-" * 40) -ForegroundColor Blue
    
    $healthScore = 0
    $totalChecks = 4
    
    # Container health
    $containerRunning = docker ps --filter name=$ContainerName --format "{{.Names}}" | Select-String $ContainerName
    if ($containerRunning) {
        Write-Host "✅ Container: Running" -ForegroundColor Green
        $healthScore++
    } else {
        Write-Host "❌ Container: Not running" -ForegroundColor Red
        return
    }
    
    # API health
    try {
        $apiResponse = Invoke-WebRequest -Uri "$BaseUrl/health" -TimeoutSec 10 -UseBasicParsing
        if ($apiResponse.StatusCode -eq 200) {
            Write-Host "✅ API: Healthy ($($apiResponse.StatusCode))" -ForegroundColor Green
            $healthScore++
        }
    } catch {
        Write-Host "❌ API: Not responding" -ForegroundColor Red
    }
    
    # Printer health
    $printerScript = @"
from zebra_print.printer.zebra_cups import ZebraCUPSPrinter
printer = ZebraCUPSPrinter()
status = printer.get_status()
if status.get('exists'):
    print(f'✅ Printer: {status.get("name", "Unknown")} ({status.get("state", "Unknown")})')
else:
    print('❌ Printer: Not found')
"@
    
    try {
        $printerResult = docker exec $ContainerName python3 -c $printerScript 2>$null
        if ($printerResult -like "*✅*") {
            Write-Host $printerResult -ForegroundColor Green
            $healthScore++
        } else {
            Write-Host $printerResult -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Printer: Check failed" -ForegroundColor Red
    }
    
    # Tunnel health
    $tunnelScript = @"
from zebra_print.database.db_manager import DatabaseManager
db = DatabaseManager('/app/data/zebra_print.db')
configs = db.get_all_tunnel_configs()
configured_tunnels = [c for c in configs if c.is_configured]
if configured_tunnels:
    config = configured_tunnels[0]
    print(f'✅ Tunnel: {config.name} configured')
    if config.domain_mapping:
        print(f'   Domain: {config.domain_mapping}')
else:
    print('❌ Tunnel: Not configured')
"@
    
    try {
        $tunnelResult = docker exec $ContainerName python3 -c $tunnelScript 2>$null
        if ($tunnelResult -like "*✅*") {
            Write-Host $tunnelResult -ForegroundColor Green
            $healthScore++
        } else {
            Write-Host $tunnelResult -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Tunnel: Check failed" -ForegroundColor Red
    }
    
    # Overall health score
    $percentage = [math]::Round(($healthScore / $totalChecks) * 100)
    Write-Host "`n📊 Overall Health: $healthScore/$totalChecks ($percentage%)" -ForegroundColor $(
        if ($percentage -ge 75) { "Green" } 
        elseif ($percentage -ge 50) { "Yellow" } 
        else { "Red" }
    )
}

function Install-WindowsService {
    Write-Host "🛠️ Windows Service Management" -ForegroundColor Blue
    
    $serviceName = "ZebraPrintControl"
    $serviceDisplayName = "Zebra Print Control System"
    
    Write-Host "This feature requires NSSM (Non-Sucking Service Manager)" -ForegroundColor Yellow
    Write-Host "Install NSSM first: choco install nssm" -ForegroundColor Yellow
    Write-Host "Or download from: https://nssm.cc/download" -ForegroundColor Yellow
    
    # This is a placeholder for service installation
    Write-Host "Service installation not yet implemented in this version" -ForegroundColor Yellow
}

function Set-FirewallRules {
    Write-Host "🔥 Configuring Windows Firewall..." -ForegroundColor Blue
    
    try {
        # Check if running as administrator
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
        
        if (-not $isAdmin) {
            Write-Host "❌ Administrator privileges required for firewall configuration" -ForegroundColor Red
            Write-Host "Run PowerShell as Administrator and try again" -ForegroundColor Yellow
            return
        }
        
        # Create firewall rules for ports 5000 and 631
        New-NetFirewallRule -DisplayName "Zebra Print API" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "Zebra Print CUPS" -Direction Inbound -Port 631 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        
        Write-Host "✅ Firewall rules configured for ports 5000 and 631" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to configure firewall: $_" -ForegroundColor Red
    }
}

function New-DesktopShortcuts {
    Write-Host "🖥️ Creating desktop shortcuts..." -ForegroundColor Blue
    
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $scriptPath = $PSScriptRoot
    
    # Create shortcuts for common commands
    $shortcuts = @(
        @{Name = "Zebra Control Panel"; Command = "shell"}
        @{Name = "Zebra Status"; Command = "status"}
        @{Name = "Zebra Health Check"; Command = "health"}
    )
    
    foreach ($shortcut in $shortcuts) {
        $shortcutPath = Join-Path $desktopPath "$($shortcut.Name).lnk"
        $WScriptShell = New-Object -ComObject WScript.Shell
        $shortcutObj = $WScriptShell.CreateShortcut($shortcutPath)
        $shortcutObj.TargetPath = "powershell.exe"
        $shortcutObj.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$scriptPath\zebra.ps1`" $($shortcut.Command)"
        $shortcutObj.WorkingDirectory = $scriptPath
        $shortcutObj.IconLocation = "shell32.dll,13"
        $shortcutObj.Save()
    }
    
    Write-Host "✅ Desktop shortcuts created" -ForegroundColor Green
}

# Main command processing
switch ($Command.ToLower()) {
    "start" {
        Test-Requirements
        Start-System
    }
    "stop" {
        Stop-System
    }
    "restart" {
        Test-Requirements
        Stop-System
        Start-Sleep -Seconds 3
        Start-System
    }
    "status" {
        Show-Status
    }
    "domain" {
        Set-CustomDomain -DomainName $Domain
    }
    "health" {
        Test-SystemHealth
    }
    "service" {
        Install-WindowsService
    }
    "firewall" {
        Set-FirewallRules
    }
    "desktop" {
        New-DesktopShortcuts
    }
    "help" {
        Write-Help
    }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\zebra.ps1 help' for usage information" -ForegroundColor Yellow
    }
}