#!/bin/bash
set -e

# Zebra Print Control System - Linux Management Script
# Provides easy management of the containerized printing system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Container name
CONTAINER_NAME="zebra-print-control"

print_banner() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║         🦓 ZEBRA PRINT CONTROL SYSTEM        ║${NC}"
    echo -e "${PURPLE}║              Linux Management CLI            ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════╝${NC}"
    echo
}

print_help() {
    print_banner
    echo -e "${CYAN}Usage: $0 <command>${NC}"
    echo
    echo -e "${YELLOW}🚀 Container Management:${NC}"
    echo "  start     - Build and start the system"
    echo "  stop      - Stop the system"
    echo "  restart   - Restart the system"
    echo "  status    - Show system status"
    echo "  logs      - Show container logs"
    echo "  shell     - Access container shell"
    echo
    echo -e "${YELLOW}🔧 Configuration:${NC}"
    echo "  setup     - Interactive setup wizard"
    echo "  domain    - Configure custom domain"
    echo "  tunnel    - Manage tunnel configuration"
    echo
    echo -e "${YELLOW}🧪 Testing & Maintenance:${NC}"
    echo "  test      - Run system tests"
    echo "  clean     - Clean up containers and images"
    echo "  backup    - Backup configuration"
    echo "  restore   - Restore configuration"
    echo
    echo -e "${YELLOW}📊 Monitoring:${NC}"
    echo "  health    - Check system health"
    echo "  printer   - Check printer status"
    echo "  api       - Test API endpoints"
    echo
    echo -e "${YELLOW}ℹ️ Information:${NC}"
    echo "  help      - Show this help"
    echo "  version   - Show version info"
    echo
}

check_requirements() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not available${NC}"
        echo "Please install Docker with Compose plugin: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

start_system() {
    echo -e "${BLUE}🚀 Starting Zebra Print Control System...${NC}"
    
    # Check for USB devices
    if lsusb | grep -i zebra &> /dev/null; then
        echo -e "${GREEN}✅ Zebra printer detected${NC}"
    else
        echo -e "${YELLOW}⚠️ No Zebra printer detected (will try to detect in container)${NC}"
    fi
    
    # Start with docker compose
    if [ -f "docker-compose.yml" ]; then
        docker compose up -d --build
    else
        echo -e "${RED}❌ docker-compose.yml not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ System started successfully!${NC}"
    echo
    echo -e "${CYAN}🌐 Services available at:${NC}"
    echo "  • API Server:    http://localhost:5000"
    echo "  • Health Check:  http://localhost:5000/health"
    echo "  • CUPS Admin:    http://localhost:8631"
    echo
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo "  • Run: $0 setup    (for initial configuration)"
    echo "  • Run: $0 status   (to check system status)"
    echo "  • Run: $0 shell    (to access control panel)"
}

stop_system() {
    echo -e "${BLUE}🛑 Stopping Zebra Print Control System...${NC}"
    docker compose down
    echo -e "${GREEN}✅ System stopped${NC}"
}

restart_system() {
    echo -e "${BLUE}🔄 Restarting system...${NC}"
    stop_system
    sleep 2
    start_system
}

show_status() {
    echo -e "${BLUE}📊 System Status:${NC}"
    echo
    
    if docker compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Container Status: Running${NC}"
        
        # API Health Check
        if curl -f http://localhost:5000/health &> /dev/null; then
            echo -e "${GREEN}✅ API Server: Healthy${NC}"
        else
            echo -e "${RED}❌ API Server: Not responding${NC}"
        fi
        
        # Show container stats
        echo
        echo -e "${CYAN}📈 Container Stats:${NC}"
        docker stats --no-stream --format "table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}" $CONTAINER_NAME 2>/dev/null || echo "Stats unavailable"
        
    else
        echo -e "${RED}❌ Container Status: Stopped${NC}"
    fi
    
    echo
    echo -e "${CYAN}🗄️ Data Volumes:${NC}"
    docker volume ls | grep zebra || echo "No volumes found"
}

show_logs() {
    echo -e "${BLUE}📋 Container Logs:${NC}"
    docker compose logs -f --tail=50
}

access_shell() {
    echo -e "${BLUE}🐚 Accessing container shell...${NC}"
    echo -e "${YELLOW}💡 Tip: Run 'python3 zebra_control_v2.py' for the control panel${NC}"
    echo
    docker exec -it $CONTAINER_NAME /bin/bash
}

interactive_setup() {
    echo -e "${BLUE}🔧 Interactive Setup Wizard${NC}"
    echo
    
    if ! docker ps | grep -q $CONTAINER_NAME; then
        echo -e "${RED}❌ Container not running. Start it first with: $0 start${NC}"
        exit 1
    fi
    
    echo -e "${CYAN}Starting setup wizard...${NC}"
    docker exec -it $CONTAINER_NAME python3 zebra_control_v2.py
}

configure_domain() {
    echo -e "${BLUE}🌐 Domain Configuration${NC}"
    echo
    
    if ! docker ps | grep -q $CONTAINER_NAME; then
        echo -e "${RED}❌ Container not running. Start it first with: $0 start${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Enter your custom domain (e.g., tln-zebra-01.abcfood.app):${NC}"
    read -r domain
    
    if [ -z "$domain" ]; then
        echo -e "${RED}❌ Domain cannot be empty${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔧 Configuring domain: $domain${NC}"
    docker exec -it $CONTAINER_NAME python3 -c "
from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
tunnel = CloudflareNamedTunnel()
success, message = tunnel.set_custom_domain('$domain')
print('✅ ' + message if success else '❌ ' + message)
if success:
    print('🔗 Webhook URL: https://$domain/print')
    print('💡 Next: Run authentication with: cloudflared tunnel login')
"
}

run_tests() {
    echo -e "${BLUE}🧪 Running System Tests...${NC}"
    
    if ! docker ps | grep -q $CONTAINER_NAME; then
        echo -e "${RED}❌ Container not running. Start it first with: $0 start${NC}"
        exit 1
    fi
    
    docker exec -it $CONTAINER_NAME python3 -m pytest tests/ -v
}

clean_system() {
    echo -e "${BLUE}🧹 Cleaning up system...${NC}"
    
    read -p "This will remove containers and images. Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose down --rmi all --volumes --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ Cleanup completed${NC}"
    else
        echo -e "${YELLOW}⚠️ Cleanup cancelled${NC}"
    fi
}

backup_config() {
    echo -e "${BLUE}💾 Backing up configuration...${NC}"
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="zebra_backup_$timestamp.tar.gz"
    
    docker run --rm -v zebra_data:/data -v $(pwd):/backup alpine tar czf /backup/$backup_file -C /data .
    
    echo -e "${GREEN}✅ Backup created: $backup_file${NC}"
}

restore_config() {
    echo -e "${BLUE}📥 Restoring configuration...${NC}"
    
    echo "Available backup files:"
    ls -la zebra_backup_*.tar.gz 2>/dev/null || echo "No backup files found"
    echo
    
    read -p "Enter backup filename: " backup_file
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Backup file not found${NC}"
        exit 1
    fi
    
    read -p "This will overwrite current configuration. Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker run --rm -v zebra_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/$backup_file"
        echo -e "${GREEN}✅ Configuration restored${NC}"
        echo -e "${YELLOW}💡 Restart the system: $0 restart${NC}"
    fi
}

check_health() {
    echo -e "${BLUE}🏥 Health Check${NC}"
    echo
    
    # Container health
    if docker ps | grep -q $CONTAINER_NAME; then
        echo -e "${GREEN}✅ Container: Running${NC}"
    else
        echo -e "${RED}❌ Container: Not running${NC}"
        return 1
    fi
    
    # API health
    if curl -f http://localhost:5000/health &> /dev/null; then
        echo -e "${GREEN}✅ API: Healthy${NC}"
        api_response=$(curl -s http://localhost:5000/health | jq -r '.status' 2>/dev/null || echo "unknown")
        echo "    Status: $api_response"
    else
        echo -e "${RED}❌ API: Not responding${NC}"
    fi
    
    # Printer status
    echo -e "${CYAN}🖨️ Checking printer...${NC}"
    docker exec $CONTAINER_NAME python3 -c "
from zebra_print.printer.zebra_cups import ZebraCUPSPrinter
printer = ZebraCUPSPrinter()
status = printer.get_status()
if status.get('exists'):
    print('✅ Printer: Found (' + status.get('name', 'Unknown') + ')')
    print('    State: ' + status.get('state', 'Unknown'))
    print('    Connection: ' + status.get('connection', 'Unknown'))
else:
    print('❌ Printer: Not found')
" 2>/dev/null || echo -e "${RED}❌ Printer: Status check failed${NC}"
}

check_printer() {
    echo -e "${BLUE}🖨️ Printer Status${NC}"
    echo
    
    if ! docker ps | grep -q $CONTAINER_NAME; then
        echo -e "${RED}❌ Container not running${NC}"
        exit 1
    fi
    
    docker exec -it $CONTAINER_NAME python3 -c "
from zebra_print.main import ZebraPrintApplication
app = ZebraPrintApplication()
status = app.printer_service.get_status()

print('📋 Printer Information:')
for key, value in status.items():
    icon = '✅' if value in [True, 'idle', 'USB'] else '❌' if value in [False, 'disabled'] else 'ℹ️'
    print(f'  {icon} {key.replace(\"_\", \" \").title()}: {value}')

print()
print('🧪 Testing printer connection...')
success, message = app.printer_service.test_connection()
print(f'{"✅" if success else "❌"} {message}')
"
}

test_api() {
    echo -e "${BLUE}🌐 API Endpoint Tests${NC}"
    echo
    
    base_url="http://localhost:5000"
    
    echo "Testing endpoints..."
    
    # Health check
    if curl -f "$base_url/health" &> /dev/null; then
        echo -e "${GREEN}✅ GET /health${NC}"
    else
        echo -e "${RED}❌ GET /health${NC}"
    fi
    
    # Printer status
    if curl -f "$base_url/printer/status" &> /dev/null; then
        echo -e "${GREEN}✅ GET /printer/status${NC}"
    else
        echo -e "${RED}❌ GET /printer/status${NC}"
    fi
    
    # Print endpoint (test with sample data)
    echo -e "${BLUE}🧪 Testing print endpoint...${NC}"
    test_response=$(curl -s -X POST "$base_url/print" \
        -H "Content-Type: application/json" \
        -d '{
            "labels": [{
                "title": "API-TEST",
                "date": "08/08/25",
                "qr_code": "TEST123"
            }]
        }' | head -200)
    
    if echo "$test_response" | grep -q "success\|printed"; then
        echo -e "${GREEN}✅ POST /print${NC}"
    else
        echo -e "${RED}❌ POST /print${NC}"
        echo "Response: $test_response"
    fi
}

show_version() {
    echo -e "${BLUE}📋 Version Information${NC}"
    echo
    echo "Zebra Print Control System v2.0"
    echo "Docker Management Script"
    echo
    echo "Components:"
    echo "  • Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
    echo "  • Docker Compose: $(docker-compose --version 2>/dev/null || echo 'Not installed')"
    echo
    
    if docker ps | grep -q $CONTAINER_NAME; then
        echo "Container Info:"
        docker exec $CONTAINER_NAME python3 --version 2>/dev/null || echo "Python: Unknown"
        docker exec $CONTAINER_NAME cloudflared --version 2>/dev/null | head -1 || echo "Cloudflared: Not installed"
    fi
}

# Main script logic
case "$1" in
    "start")
        check_requirements
        start_system
        ;;
    "stop")
        stop_system
        ;;
    "restart")
        check_requirements
        restart_system
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "shell")
        access_shell
        ;;
    "setup")
        interactive_setup
        ;;
    "domain")
        configure_domain
        ;;
    "tunnel")
        interactive_setup
        ;;
    "test")
        run_tests
        ;;
    "clean")
        clean_system
        ;;
    "backup")
        backup_config
        ;;
    "restore")
        restore_config
        ;;
    "health")
        check_health
        ;;
    "printer")
        check_printer
        ;;
    "api")
        test_api
        ;;
    "version")
        show_version
        ;;
    "help"|"--help"|"-h"|"")
        print_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac