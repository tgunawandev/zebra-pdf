#!/bin/bash
set -e

# Zebra Print Control System - Quick Run Script
# Downloads and runs the pre-built Docker image from Docker Hub

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DOCKER_IMAGE="kodemeio/zebra-pdf:latest"
CONTAINER_NAME="zebra-print-control"

print_banner() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║         🦓 ZEBRA PRINT CONTROL SYSTEM        ║${NC}"
    echo -e "${PURPLE}║              Quick Run (Docker Hub)          ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════╝${NC}"
    echo
}

check_requirements() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
}

check_usb_printer() {
    if lsusb | grep -i zebra &> /dev/null; then
        echo -e "${GREEN}✅ Zebra printer detected${NC}"
    else
        echo -e "${YELLOW}⚠️ No Zebra printer detected${NC}"
        echo -e "${CYAN}💡 Make sure your Zebra printer is connected via USB${NC}"
    fi
}

stop_existing() {
    if docker ps -a | grep -q $CONTAINER_NAME; then
        echo -e "${BLUE}🛑 Stopping existing container...${NC}"
        docker stop $CONTAINER_NAME &> /dev/null || true
        docker rm $CONTAINER_NAME &> /dev/null || true
    fi
}

pull_and_run() {
    echo -e "${BLUE}📥 Pulling latest image from Docker Hub...${NC}"
    docker pull $DOCKER_IMAGE
    
    echo -e "${BLUE}🚀 Starting Zebra Print Control System...${NC}"
    
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        --privileged \
        --pull always \
        --device=/dev/bus/usb:/dev/bus/usb \
        -p 5000:5000 \
        -p 8631:631 \
        -v zebra_data:/app/data \
        -v zebra_logs:/var/log/zebra-print \
        -v /dev:/dev:ro \
        -e ZEBRA_API_HOST=0.0.0.0 \
        -e ZEBRA_API_PORT=5000 \
        -e ZEBRA_PRINTER_NAME=ZTC-ZD230-203dpi-ZPL \
        -e TZ=UTC \
        $DOCKER_IMAGE
}

show_status() {
    echo -e "${GREEN}✅ System started successfully!${NC}"
    echo
    echo -e "${CYAN}🌐 Services available at:${NC}"
    echo "  • API Server:    http://localhost:5000"
    echo "  • Health Check:  http://localhost:5000/health"
    echo "  • CUPS Admin:    http://localhost:8631"
    echo
    echo -e "${YELLOW}💡 Useful commands:${NC}"
    echo "  • Check status:  docker ps"
    echo "  • View logs:     docker logs $CONTAINER_NAME"
    echo "  • Access shell:  docker exec -it $CONTAINER_NAME /bin/bash"
    echo "  • Stop system:   docker stop $CONTAINER_NAME"
    echo
    
    # Wait a moment for container to start
    sleep 3
    
    # Quick health check
    if curl -f http://localhost:5000/health &> /dev/null; then
        echo -e "${GREEN}✅ API is responding${NC}"
    else
        echo -e "${YELLOW}⏳ API starting up... (check logs if it doesn't respond in 30s)${NC}"
    fi
}

# Main execution
print_banner

# Check if help requested
if [[ "$1" == "help" || "$1" == "--help" || "$1" == "-h" ]]; then
    echo -e "${CYAN}This script downloads and runs the Zebra Print Control System${NC}"
    echo -e "${CYAN}from a pre-built Docker image hosted on Docker Hub.${NC}"
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0           - Download and run the system"
    echo "  $0 help      - Show this help"
    echo
    echo -e "${YELLOW}Requirements:${NC}"
    echo "  • Docker installed and running"
    echo "  • USB Zebra printer connected (optional)"
    echo "  • Ports 5000 and 8631 available"
    exit 0
fi

check_requirements
check_usb_printer
stop_existing
pull_and_run
show_status