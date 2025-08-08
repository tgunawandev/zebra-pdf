@echo off
setlocal enabledelayedexpansion

REM Zebra Print Control System - Windows Management Script
REM Provides easy management of the containerized printing system

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set CONTAINER_NAME=zebra-print-control

REM Colors (using PowerShell for Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

goto main

:print_banner
echo.
echo %PURPLE%^╔══════════════════════════════════════════════^╗%NC%
echo %PURPLE%^║         🦓 ZEBRA PRINT CONTROL SYSTEM        ^║%NC%
echo %PURPLE%^║             Windows Management CLI            ^║%NC%
echo %PURPLE%^╚══════════════════════════════════════════════^╝%NC%
echo.
goto :eof

:print_help
call :print_banner
echo %CYAN%Usage: %~nx0 ^<command^>%NC%
echo.
echo %YELLOW%🚀 Container Management:%NC%
echo   start     - Build and start the system
echo   stop      - Stop the system
echo   restart   - Restart the system
echo   status    - Show system status
echo   logs      - Show container logs
echo   shell     - Access container shell
echo.
echo %YELLOW%🔧 Configuration:%NC%
echo   setup     - Interactive setup wizard
echo   domain    - Configure custom domain
echo   tunnel    - Manage tunnel configuration
echo.
echo %YELLOW%🧪 Testing ^& Maintenance:%NC%
echo   test      - Run system tests
echo   clean     - Clean up containers and images
echo   backup    - Backup configuration
echo   restore   - Restore configuration
echo.
echo %YELLOW%📊 Monitoring:%NC%
echo   health    - Check system health
echo   printer   - Check printer status
echo   api       - Test API endpoints
echo.
echo %YELLOW%ℹ️ Information:%NC%
echo   help      - Show this help
echo   version   - Show version info
echo.
goto :eof

:check_requirements
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Docker is not installed%NC%
    echo Please install Docker Desktop: https://docs.docker.com/desktop/windows/
    exit /b 1
)

docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Docker Compose is not available%NC%
    echo Please ensure Docker Desktop is properly installed
    exit /b 1
)
goto :eof

:start_system
echo %BLUE%🚀 Starting Zebra Print Control System...%NC%

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo %RED%❌ docker-compose.yml not found%NC%
    exit /b 1
)

REM Start with docker compose
docker compose up -d --build
if %errorlevel% neq 0 (
    echo %RED%❌ Failed to start system%NC%
    exit /b 1
)

echo %GREEN%✅ System started successfully!%NC%
echo.
echo %CYAN%🌐 Services available at:%NC%
echo   • API Server:    http://localhost:5000
echo   • Health Check:  http://localhost:5000/health
echo   • CUPS Admin:    http://localhost:8631
echo.
echo %YELLOW%💡 Next steps:%NC%
echo   • Run: %~nx0 setup    (for initial configuration)
echo   • Run: %~nx0 status   (to check system status)
echo   • Run: %~nx0 shell    (to access control panel)
goto :eof

:stop_system
echo %BLUE%🛑 Stopping Zebra Print Control System...%NC%
docker compose down
echo %GREEN%✅ System stopped%NC%
goto :eof

:restart_system
echo %BLUE%🔄 Restarting system...%NC%
call :stop_system
timeout /t 3 /nobreak >nul
call :start_system
goto :eof

:show_status
echo %BLUE%📊 System Status:%NC%
echo.

docker ps --filter name=%CONTAINER_NAME% --format "table {{.Names}}\t{{.Status}}" | findstr %CONTAINER_NAME% >nul
if %errorlevel% equ 0 (
    echo %GREEN%✅ Container Status: Running%NC%
    
    REM API Health Check
    curl -f http://localhost:5000/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo %GREEN%✅ API Server: Healthy%NC%
    ) else (
        echo %RED%❌ API Server: Not responding%NC%
    )
    
    echo.
    echo %CYAN%📈 Container Stats:%NC%
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" %CONTAINER_NAME% 2>nul
    
) else (
    echo %RED%❌ Container Status: Stopped%NC%
)

echo.
echo %CYAN%🗄️ Data Volumes:%NC%
docker volume ls | findstr zebra
goto :eof

:show_logs
echo %BLUE%📋 Container Logs:%NC%
docker compose logs -f --tail=50
goto :eof

:access_shell
echo %BLUE%🐚 Accessing container shell...%NC%
echo %YELLOW%💡 Tip: Run 'python3 zebra_control_v2.py' for the control panel%NC%
echo.
docker exec -it %CONTAINER_NAME% /bin/bash
goto :eof

:interactive_setup
echo %BLUE%🔧 Interactive Setup Wizard%NC%
echo.

docker ps --filter name=%CONTAINER_NAME% --format "{{.Names}}" | findstr %CONTAINER_NAME% >nul
if %errorlevel% neq 0 (
    echo %RED%❌ Container not running. Start it first with: %~nx0 start%NC%
    exit /b 1
)

echo %CYAN%Starting setup wizard...%NC%
docker exec -it %CONTAINER_NAME% python3 zebra_control_v2.py
goto :eof

:configure_domain
echo %BLUE%🌐 Domain Configuration%NC%
echo.

docker ps --filter name=%CONTAINER_NAME% --format "{{.Names}}" | findstr %CONTAINER_NAME% >nul
if %errorlevel% neq 0 (
    echo %RED%❌ Container not running. Start it first with: %~nx0 start%NC%
    exit /b 1
)

set /p domain=%YELLOW%Enter your custom domain (e.g., tln-zebra-01.abcfood.app): %NC%

if "%domain%"=="" (
    echo %RED%❌ Domain cannot be empty%NC%
    exit /b 1
)

echo %BLUE%🔧 Configuring domain: %domain%%NC%
docker exec -it %CONTAINER_NAME% python3 -c "from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel; tunnel = CloudflareNamedTunnel(); success, message = tunnel.set_custom_domain('%domain%'); print('✅ ' + message if success else '❌ ' + message); print('🔗 Webhook URL: https://%domain%/print') if success else None; print('💡 Next: Run authentication with: cloudflared tunnel login') if success else None"
goto :eof

:run_tests
echo %BLUE%🧪 Running System Tests...%NC%

docker ps --filter name=%CONTAINER_NAME% --format "{{.Names}}" | findstr %CONTAINER_NAME% >nul
if %errorlevel% neq 0 (
    echo %RED%❌ Container not running. Start it first with: %~nx0 start%NC%
    exit /b 1
)

docker exec -it %CONTAINER_NAME% python3 -m pytest tests/ -v
goto :eof

:clean_system
echo %BLUE%🧹 Cleaning up system...%NC%

set /p confirm=This will remove containers and images. Continue? (y/N): 
if /i "%confirm%"=="y" (
    docker compose down --rmi all --volumes --remove-orphans
    docker system prune -f
    echo %GREEN%✅ Cleanup completed%NC%
) else (
    echo %YELLOW%⚠️ Cleanup cancelled%NC%
)
goto :eof

:backup_config
echo %BLUE%💾 Backing up configuration...%NC%

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%%datetime:~12,2%
set backup_file=zebra_backup_%timestamp%.tar.gz

docker run --rm -v zebra_data:/data -v "%cd%":/backup alpine tar czf /backup/%backup_file% -C /data .

echo %GREEN%✅ Backup created: %backup_file%%NC%
goto :eof

:restore_config
echo %BLUE%📥 Restoring configuration...%NC%

echo Available backup files:
dir zebra_backup_*.tar.gz 2>nul
echo.

set /p backup_file=Enter backup filename: 

if not exist "%backup_file%" (
    echo %RED%❌ Backup file not found%NC%
    exit /b 1
)

set /p confirm=This will overwrite current configuration. Continue? (y/N): 
if /i "%confirm%"=="y" (
    docker run --rm -v zebra_data:/data -v "%cd%":/backup alpine sh -c "cd /data && tar xzf /backup/%backup_file%"
    echo %GREEN%✅ Configuration restored%NC%
    echo %YELLOW%💡 Restart the system: %~nx0 restart%NC%
)
goto :eof

:check_health
echo %BLUE%🏥 Health Check%NC%
echo.

REM Container health
docker ps --filter name=%CONTAINER_NAME% --format "{{.Names}}" | findstr %CONTAINER_NAME% >nul
if %errorlevel% equ 0 (
    echo %GREEN%✅ Container: Running%NC%
) else (
    echo %RED%❌ Container: Not running%NC%
    exit /b 1
)

REM API health
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✅ API: Healthy%NC%
) else (
    echo %RED%❌ API: Not responding%NC%
)

REM Printer status
echo %CYAN%🖨️ Checking printer...%NC%
docker exec %CONTAINER_NAME% python3 -c "from zebra_print.printer.zebra_cups import ZebraCUPSPrinter; printer = ZebraCUPSPrinter(); status = printer.get_status(); print('✅ Printer: Found (' + status.get('name', 'Unknown') + ')') if status.get('exists') else print('❌ Printer: Not found'); print('    State: ' + status.get('state', 'Unknown')) if status.get('exists') else None; print('    Connection: ' + status.get('connection', 'Unknown')) if status.get('exists') else None" 2>nul
goto :eof

:check_printer
echo %BLUE%🖨️ Printer Status%NC%
echo.

docker ps --filter name=%CONTAINER_NAME% --format "{{.Names}}" | findstr %CONTAINER_NAME% >nul
if %errorlevel% neq 0 (
    echo %RED%❌ Container not running%NC%
    exit /b 1
)

docker exec -it %CONTAINER_NAME% python3 -c "from zebra_print.main import ZebraPrintApplication; app = ZebraPrintApplication(); status = app.printer_service.get_status(); print('📋 Printer Information:'); [print(f'  {"✅" if value in [True, "idle", "USB"] else "❌" if value in [False, "disabled"] else "ℹ️"} {key.replace("_", " ").title()}: {value}') for key, value in status.items()]; print(); print('🧪 Testing printer connection...'); success, message = app.printer_service.test_connection(); print(f'{"✅" if success else "❌"} {message}')"
goto :eof

:test_api
echo %BLUE%🌐 API Endpoint Tests%NC%
echo.

set base_url=http://localhost:5000

echo Testing endpoints...

REM Health check
curl -f "%base_url%/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✅ GET /health%NC%
) else (
    echo %RED%❌ GET /health%NC%
)

REM Printer status
curl -f "%base_url%/printer/status" >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✅ GET /printer/status%NC%
) else (
    echo %RED%❌ GET /printer/status%NC%
)

echo %BLUE%🧪 Testing print endpoint...%NC%
curl -s -X POST "%base_url%/print" -H "Content-Type: application/json" -d "{\"labels\":[{\"title\":\"API-TEST\",\"date\":\"08/08/25\",\"qr_code\":\"TEST123\"}]}" | findstr /i "success printed" >nul
if %errorlevel% equ 0 (
    echo %GREEN%✅ POST /print%NC%
) else (
    echo %RED%❌ POST /print%NC%
)
goto :eof

:show_version
echo %BLUE%📋 Version Information%NC%
echo.
echo Zebra Print Control System v2.0
echo Docker Management Script (Windows)
echo.
echo Components:
docker --version 2>nul || echo   • Docker: Not installed
docker-compose --version 2>nul || echo   • Docker Compose: Not installed
echo.

docker ps --filter name=%CONTAINER_NAME% --format "{{.Names}}" | findstr %CONTAINER_NAME% >nul
if %errorlevel% equ 0 (
    echo Container Info:
    docker exec %CONTAINER_NAME% python3 --version 2>nul || echo Python: Unknown
    docker exec %CONTAINER_NAME% cloudflared --version 2>nul | findstr cloudflared || echo Cloudflared: Not installed
)
goto :eof

:main
REM Main script logic
if "%~1"=="start" (
    call :check_requirements
    call :start_system
) else if "%~1"=="stop" (
    call :stop_system
) else if "%~1"=="restart" (
    call :check_requirements
    call :restart_system
) else if "%~1"=="status" (
    call :show_status
) else if "%~1"=="logs" (
    call :show_logs
) else if "%~1"=="shell" (
    call :access_shell
) else if "%~1"=="setup" (
    call :interactive_setup
) else if "%~1"=="domain" (
    call :configure_domain
) else if "%~1"=="tunnel" (
    call :interactive_setup
) else if "%~1"=="test" (
    call :run_tests
) else if "%~1"=="clean" (
    call :clean_system
) else if "%~1"=="backup" (
    call :backup_config
) else if "%~1"=="restore" (
    call :restore_config
) else if "%~1"=="health" (
    call :check_health
) else if "%~1"=="printer" (
    call :check_printer
) else if "%~1"=="api" (
    call :test_api
) else if "%~1"=="version" (
    call :show_version
) else if "%~1"=="help" (
    call :print_help
) else if "%~1"=="--help" (
    call :print_help
) else if "%~1"=="-h" (
    call :print_help
) else if "%~1"=="" (
    call :print_help
) else (
    echo %RED%❌ Unknown command: %~1%NC%
    echo Run '%~nx0 help' for usage information
    exit /b 1
)

endlocal