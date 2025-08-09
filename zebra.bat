@echo off
setlocal enabledelayedexpansion

rem Zebra Print Control System - Windows Management Script
rem Provides easy management of the Python-based printing system

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

rem Container name (not used in direct Python version)
set "CONTAINER_NAME=zebra-print-control"

call :print_banner
goto :main

:print_banner
echo ============================================
echo       ZEBRA PRINT CONTROL SYSTEM         
echo           Windows Management CLI          
echo ============================================
echo.
goto :eof

:print_help
call :print_banner
echo Usage: %0 ^<command^>
echo.
echo System Management:
echo   start     - Start the Python application
echo   stop      - Stop the Python application
echo   restart   - Restart the Python application
echo   status    - Show system status
echo   shell     - Run interactive control panel
echo.
echo Configuration:
echo   setup     - Interactive setup wizard
echo   domain    - Configure custom domain
echo   tunnel    - Manage tunnel configuration
echo   auth      - Setup Cloudflare authentication
echo.
echo Testing ^& Maintenance:
echo   test      - Run system tests
echo   printer   - Check printer status
echo   api       - Test API endpoints
echo   health    - Check system health
echo.
echo Information:
echo   install   - Check installation requirements
echo   help      - Show this help
echo   version   - Show version info
echo.
goto :eof

:check_requirements
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python: https://www.python.org/downloads/
    exit /b 1
)

if not exist "%SCRIPT_DIR%zebra_control_v2.py" (
    echo ERROR: zebra_control_v2.py not found in current directory
    echo Please ensure all Python files are present
    exit /b 1
)

if not exist "%SCRIPT_DIR%requirements.txt" (
    echo WARNING: requirements.txt not found
    echo You may need to install Python dependencies manually
)
goto :eof

:start_system
echo Starting Zebra Print Control System...

call :check_requirements
if %errorlevel% neq 0 exit /b 1

rem Check if process is already running
tasklist /fi "windowtitle eq Zebra*" 2>nul | find /i "python" >nul
if %errorlevel% equ 0 (
    echo WARNING: Zebra system appears to be already running
)

echo Starting Python application...
start "Zebra Print Control" python zebra_control_v2.py

timeout /t 3 >nul

rem Check if API server is responding
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: System started successfully!
    echo.
    echo Services available at:
    echo   * API Server:    http://localhost:5000
    echo   * Health Check:  http://localhost:5000/health
    echo   * CUPS Admin:    http://localhost:8631
) else (
    echo INFO: System starting... API may take a moment to be ready
)

echo.
echo Next steps:
echo   * Run: %0 setup    (for initial configuration)
echo   * Run: %0 status   (to check system status)
echo   * Run: %0 shell    (to access control panel)
goto :eof

:stop_system
echo Stopping Zebra Print Control System...

rem Kill Python processes with zebra in the window title
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq Zebra*" /fo table /nh 2^>nul') do (
    if not "%%i"=="INFO:" (
        taskkill /pid %%i /f >nul 2>&1
        echo Stopped process %%i
    )
)

rem Also try to kill by process name if running as service
tasklist | find /i "python.exe" >nul
if %errorlevel% equ 0 (
    echo INFO: Python processes still running, you may need to stop them manually
)

echo SUCCESS: System stopped
goto :eof

:restart_system
echo Restarting system...
call :stop_system
timeout /t 2 >nul
call :start_system
goto :eof

:show_status
echo System Status:
echo.

rem Check if Python process is running
tasklist /fi "windowtitle eq Zebra*" 2>nul | find /i "python" >nul
if %errorlevel% equ 0 (
    echo SUCCESS: Python Process: Running
) else (
    echo ERROR: Python Process: Not running
)

rem API Health Check
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: API Server: Healthy
) else (
    echo ERROR: API Server: Not responding
)

rem Check if port 5000 is in use
netstat -an | find ":5000" >nul
if %errorlevel% equ 0 (
    echo INFO: Port 5000: In use
) else (
    echo WARNING: Port 5000: Available
)

echo.
echo Data Directory: %SCRIPT_DIR%
if exist "%SCRIPT_DIR%logs" (
    echo Logs Directory: %SCRIPT_DIR%logs
) else (
    echo WARNING: No logs directory found
)
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
echo Domain Configuration
echo.

call :check_requirements
if %errorlevel% neq 0 exit /b 1

set /p domain="Enter your custom domain (e.g., tln-zebra-01.abcfood.app): "

if "%domain%"=="" (
    echo ERROR: Domain cannot be empty
    exit /b 1
)

echo Configuring domain: %domain%
python -c "from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel; tunnel = CloudflareNamedTunnel(); success, message = tunnel.set_custom_domain('%domain%'); print('SUCCESS: ' + message if success else 'ERROR: ' + message); print('Webhook URL: https://%domain%/print') if success else None; print('Next: Run authentication with: cloudflared tunnel login') if success else None"
goto :eof

:run_tests
echo Running System Tests...

call :check_requirements
if %errorlevel% neq 0 exit /b 1

if exist "%SCRIPT_DIR%tests" (
    python -m pytest tests/ -v
) else (
    echo WARNING: No tests directory found
    echo Running basic system checks instead...
    call :check_health
)
goto :eof




:check_health
echo Health Check
echo.

rem Python availability
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: Python: Available
    python --version
) else (
    echo ERROR: Python: Not available
    exit /b 1
)

rem API health
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: API: Healthy
    curl -s http://localhost:5000/health
) else (
    echo ERROR: API: Not responding
)

rem Printer status
echo INFO: Checking printer...
python -c "try: from zebra_print.printer.zebra_cups import ZebraCUPSPrinter; printer = ZebraCUPSPrinter(); status = printer.get_status(); print('SUCCESS: Printer Found (' + status.get('name', 'Unknown') + ')' if status.get('exists') else 'ERROR: Printer Not found'); print('State: ' + status.get('state', 'Unknown')); print('Connection: ' + status.get('connection', 'Unknown')) except Exception as e: print('ERROR: Printer status check failed:', e)"
goto :eof

:check_printer
echo Printer Status
echo.

call :check_requirements
if %errorlevel% neq 0 exit /b 1

python -c "from zebra_print.main import ZebraPrintApplication; app = ZebraPrintApplication(); status = app.printer_service.get_status(); print('Printer Information:'); [print(f'  {\"SUCCESS\" if value in [True, \"idle\", \"USB\"] else \"ERROR\" if value in [False, \"disabled\"] else \"INFO\"}: {key.replace(\"_\", \" \").title()}: {value}') for key, value in status.items()]; print(); print('Testing printer connection...'); success, message = app.printer_service.test_connection(); print(f'{\"SUCCESS\" if success else \"ERROR\"}: {message}')"
goto :eof

:test_api
echo API Endpoint Tests
echo.

set "base_url=http://localhost:5000"

echo Testing endpoints...

rem Health check
curl -f "%base_url%/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: GET /health
) else (
    echo ERROR: GET /health
)

rem Printer status
curl -f "%base_url%/printer/status" >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: GET /printer/status
) else (
    echo ERROR: GET /printer/status
)

rem Print endpoint test
echo INFO: Testing print endpoint...
curl -s -X POST "%base_url%/print" -H "Content-Type: application/json" -d "{\"labels\": [{\"title\": \"API-TEST\", \"date\": \"08/08/25\", \"qr_code\": \"TEST123\"}]}" | find "success" >nul
if %errorlevel% equ 0 (
    echo SUCCESS: POST /print
) else (
    echo ERROR: POST /print
)
goto :eof

:show_version
echo Version Information
echo.
echo Zebra Print Control System v2.0
echo Windows Management Script
echo.
echo Components:
python --version 2>nul || echo Python: Not installed
curl --version 2>nul | findstr curl || echo cURL: Not installed
cloudflared --version 2>nul | findstr cloudflared || echo Cloudflared: Not installed
echo.
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
) else if "%~1"=="shell" (
    call :access_shell
) else if "%~1"=="setup" (
    call :interactive_setup
) else if "%~1"=="domain" (
    call :configure_domain
) else if "%~1"=="tunnel" (
    call :interactive_setup
) else if "%~1"=="auth" (
    echo Running Cloudflare authentication...
    if exist "cloudflare-auth.bat" (
        call cloudflare-auth.bat
    ) else (
        echo INFO: cloudflare-auth.bat not found, running manual auth
        cloudflared tunnel login
    )
) else if "%~1"=="test" (
    call :run_tests
) else if "%~1"=="health" (
    call :check_health
) else if "%~1"=="printer" (
    call :check_printer
) else if "%~1"=="api" (
    call :test_api
) else if "%~1"=="install" (
    call :check_requirements
) else if "%~1"=="check" (
    call :check_requirements
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
    echo ERROR: Unknown command: %~1
    echo Run '%0 help' for usage information
    exit /b 1
)

:end