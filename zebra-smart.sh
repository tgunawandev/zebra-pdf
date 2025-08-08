#!/bin/bash
set -e

# Zebra Print Control System - Smart Port Management
# Automatically handles port conflicts and finds available ports

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Container name
CONTAINER_NAME="zebra-print-control"

# Function to find free port
find_free_port() {
    local start_port=$1
    local max_port=${2:-$((start_port + 100))}
    
    for port in $(seq $start_port $max_port); do
        if ! netstat -tln 2>/dev/null | grep -q ":$port " && ! ss -tln 2>/dev/null | grep -q ":$port "; then
            echo $port
            return 0
        fi
    done
    
    echo $start_port  # fallback
    return 1
}

# Smart port detection
detect_and_set_ports() {
    echo -e "${BLUE}🔍 Detecting available ports...${NC}"
    
    # Default ports
    local api_port=5000
    local cups_port=8631
    
    # Check API port
    if netstat -tln 2>/dev/null | grep -q ":$api_port " || ss -tln 2>/dev/null | grep -q ":$api_port "; then
        echo -e "${YELLOW}⚠️ Port $api_port (API) is in use${NC}"
        api_port=$(find_free_port 5001)
        echo -e "${GREEN}✅ Using port $api_port for API${NC}"
    else
        echo -e "${GREEN}✅ Port $api_port (API) available${NC}"
    fi
    
    # Check CUPS port  
    if netstat -tln 2>/dev/null | grep -q ":$cups_port " || ss -tln 2>/dev/null | grep -q ":$cups_port "; then
        echo -e "${YELLOW}⚠️ Port $cups_port (CUPS) is in use${NC}"
        cups_port=$(find_free_port 8632)
        echo -e "${GREEN}✅ Using port $cups_port for CUPS${NC}"
    else
        echo -e "${GREEN}✅ Port $cups_port (CUPS) available${NC}"
    fi
    
    # Export for docker-compose
    export ZEBRA_API_PORT=$api_port
    export ZEBRA_CUPS_PORT=$cups_port
    export ZEBRA_CONTAINER_API_PORT=5000  # Always 5000 inside container
    
    echo -e "${CYAN}📊 Port Configuration:${NC}"
    echo "  • Host API Port:  $api_port → Container 5000"
    echo "  • Host CUPS Port: $cups_port → Container 631"
}

start_system() {
    echo -e "${BLUE}🚀 Starting Zebra Print Control System (Smart Mode)...${NC}"
    
    # Smart port detection
    detect_and_set_ports
    
    # Check for USB devices
    if lsusb | grep -i zebra &> /dev/null; then
        echo -e "${GREEN}✅ Zebra printer detected${NC}"
    else
        echo -e "${YELLOW}⚠️ No Zebra printer detected (will try to detect in container)${NC}"
    fi
    
    # Start with smart docker compose
    if [ -f "docker-compose-smart.yml" ]; then
        docker compose -f docker-compose-smart.yml up -d --build
    else
        echo -e "${RED}❌ docker-compose-smart.yml not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ System started successfully!${NC}"
    echo
    echo -e "${CYAN}🌐 Services available at:${NC}"
    echo "  • API Server:    http://localhost:${ZEBRA_API_PORT}"
    echo "  • Health Check:  http://localhost:${ZEBRA_API_PORT}/health"
    echo "  • CUPS Admin:    http://localhost:${ZEBRA_CUPS_PORT}"
    echo
    echo -e "${YELLOW}💡 Ports automatically configured to avoid conflicts!${NC}"
}

stop_system() {
    echo -e "${BLUE}🛑 Stopping Zebra Print Control System...${NC}"
    docker compose -f docker-compose-smart.yml down 2>/dev/null || docker compose down
    echo -e "${GREEN}✅ System stopped${NC}"
}

show_ports() {
    echo -e "${BLUE}📊 Current Port Configuration:${NC}"
    echo
    
    if [ -f ".port-config" ]; then
        source .port-config
        echo -e "${GREEN}Configured ports:${NC}"
        echo "  • API Server:  http://localhost:${API_PORT:-5000}"
        echo "  • CUPS Admin:  http://localhost:${CUPS_PORT:-8631}"
        echo "  • Last check:  ${LAST_CHECK:-Unknown}"
    else
        echo -e "${YELLOW}No port configuration found${NC}"
        echo "Default ports:"
        echo "  • API Server:  http://localhost:5000"
        echo "  • CUPS Admin:  http://localhost:8631"
    fi
    
    echo
    echo -e "${CYAN}Current port usage:${NC}"
    if command -v netstat &> /dev/null; then
        netstat -tln | grep -E ":(5000|5001|5002|8631|8632)" || echo "  No conflicts detected"
    elif command -v ss &> /dev/null; then
        ss -tln | grep -E ":(5000|5001|5002|8631|8632)" || echo "  No conflicts detected"
    else
        echo "  Cannot check port usage (netstat/ss not available)"
    fi
}

resolve_conflicts() {
    echo -e "${BLUE}🔧 Resolving port conflicts...${NC}"
    ./find-free-port.sh
    echo -e "${YELLOW}💡 Restart system to apply changes: $0 restart${NC}"
}

# Main script logic
case "$1" in
    "start")
        start_system
        ;;
    "stop")
        stop_system
        ;;
    "restart")
        stop_system
        sleep 2
        start_system
        ;;
    "ports")
        show_ports
        ;;
    "fix-ports"|"resolve")
        resolve_conflicts
        ;;
    "help"|"--help"|"-h"|"")
        echo -e "${CYAN}Zebra Print Control - Smart Port Management${NC}"
        echo ""
        echo "Commands:"
        echo "  start     - Start with automatic port detection"
        echo "  stop      - Stop the system"
        echo "  restart   - Restart with port detection"
        echo "  ports     - Show current port configuration"
        echo "  resolve   - Fix port conflicts manually"
        echo "  help      - Show this help"
        echo ""
        echo "Features:"
        echo "  ✅ Automatic port conflict resolution"
        echo "  ✅ Dynamic port allocation"
        echo "  ✅ Preserves functionality on any port"
        echo ""
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac