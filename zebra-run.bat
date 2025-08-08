@echo off
setlocal enabledelayedexpansion

REM Zebra Print Control System - Quick Run Script (Windows)
REM Downloads and runs the pre-built Docker image from Docker Hub

set DOCKER_IMAGE=kodemeio/zebra-pdf:latest
set CONTAINER_NAME=zebra-print-control

echo.
echo ===============================================
echo          🦓 ZEBRA PRINT CONTROL SYSTEM        
echo              Quick Run (Docker Hub)           
echo ===============================================
echo.

REM Check if help requested
if "%1"=="help" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help

REM Check Docker installation
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not running
    echo Please install Docker Desktop: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

echo ✅ Docker detected

REM Stop existing container if running
docker ps -a | findstr %CONTAINER_NAME% >nul 2>&1
if not errorlevel 1 (
    echo 🛑 Stopping existing container...
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
)

REM Pull and run
echo 📥 Pulling latest image from Docker Hub...
docker pull %DOCKER_IMAGE%

echo 🚀 Starting Zebra Print Control System...
docker run -d ^
    --name %CONTAINER_NAME% ^
    --restart unless-stopped ^
    --privileged ^
    -p 5000:5000 ^
    -p 8631:631 ^
    -v zebra_data:/app/data ^
    -v zebra_logs:/var/log/zebra-print ^
    -e ZEBRA_API_HOST=0.0.0.0 ^
    -e ZEBRA_API_PORT=5000 ^
    -e ZEBRA_PRINTER_NAME=ZTC-ZD230-203dpi-ZPL ^
    -e TZ=UTC ^
    %DOCKER_IMAGE%

if errorlevel 1 (
    echo ❌ Failed to start container
    pause
    exit /b 1
)

echo.
echo ✅ System started successfully!
echo.
echo 🌐 Services available at:
echo   • API Server:    http://localhost:5000
echo   • Health Check:  http://localhost:5000/health
echo   • CUPS Admin:    http://localhost:8631
echo.
echo 💡 Useful commands:
echo   • Check status:  docker ps
echo   • View logs:     docker logs %CONTAINER_NAME%
echo   • Access shell:  docker exec -it %CONTAINER_NAME% /bin/bash
echo   • Stop system:   docker stop %CONTAINER_NAME%
echo.

REM Quick health check
timeout /t 3 /nobreak >nul 2>&1
curl -f http://localhost:5000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ API is responding
) else (
    echo ⏳ API starting up... (check logs if it doesn't respond in 30s)
)

echo.
echo Press any key to exit...
pause >nul
exit /b 0

:show_help
echo This script downloads and runs the Zebra Print Control System
echo from a pre-built Docker image hosted on Docker Hub.
echo.
echo Usage:
echo   %~nx0           - Download and run the system
echo   %~nx0 help      - Show this help
echo.
echo Requirements:
echo   • Docker Desktop installed and running
echo   • USB Zebra printer connected (optional)
echo   • Ports 5000 and 8631 available
echo.
pause
exit /b 0