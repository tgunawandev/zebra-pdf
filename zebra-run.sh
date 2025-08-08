#!/bin/bash
set -e

# Zebra Print Control System - Enhanced Quick Run Script
# Downloads and runs the pre-built Docker image from Docker Hub
# with support for environment variables, .env files, and interactive setup

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
ENV_FILE=".env"

# Command line options
SETUP_MODE=false
ENV_FILE_PATH=""
DOMAIN=""
TUNNEL_TYPE=""

print_banner() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║         🦓 ZEBRA PRINT CONTROL SYSTEM        ║${NC}"
    echo -e "${PURPLE}║              Quick Run (Docker Hub)          ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════╝${NC}"
    echo
}

print_help() {
    print_banner
    echo -e "${CYAN}This script downloads and runs the Zebra Print Control System${NC}"
    echo -e "${CYAN}from a pre-built Docker image hosted on Docker Hub.${NC}"
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0                          - Download and run the system"
    echo "  $0 --setup                  - Run with interactive setup after start"
    echo "  $0 --env-file <file>        - Use custom environment file"
    echo "  $0 --domain <domain>        - Set tunnel domain directly"
    echo "  $0 --tunnel <type>          - Set tunnel type (cloudflare/ngrok)"
    echo "  $0 --help                   - Show this help"
    echo
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo "  ZEBRA_DOMAIN                - Custom domain for tunnel"
    echo "  ZEBRA_TUNNEL_TYPE           - Tunnel type (cloudflare/ngrok)"
    echo "  CLOUDFLARE_TOKEN            - Cloudflare tunnel token"
    echo "  NGROK_AUTHTOKEN             - Ngrok authentication token"
    echo "  ZEBRA_PRINTER_NAME          - Custom printer name"
    echo
    echo -e "${YELLOW}.env File Example:${NC}"
    echo "  ZEBRA_DOMAIN=tln-zebra-01.abcfood.app"
    echo "  ZEBRA_TUNNEL_TYPE=cloudflare"
    echo "  CLOUDFLARE_TOKEN=your_token_here"
    echo
    echo -e "${YELLOW}Requirements:${NC}"
    echo "  • Docker installed and running"
    echo "  • USB Zebra printer connected (optional)"
    echo "  • Ports 5000 and 8631 available"
    exit 0
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --setup)
                SETUP_MODE=true
                shift
                ;;
            --env-file)
                ENV_FILE_PATH="$2"
                shift 2
                ;;
            --domain)
                DOMAIN="$2"
                shift 2
                ;;
            --tunnel)
                TUNNEL_TYPE="$2"
                shift 2
                ;;
            --help|-h|help)
                print_help
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

load_env_file() {
    local env_file="${ENV_FILE_PATH:-$ENV_FILE}"
    
    if [[ -f "$env_file" ]]; then
        echo -e "${BLUE}📁 Loading environment from: $env_file${NC}"
        # Source the env file, but only export ZEBRA_* and CLOUDFLARE_* and NGROK_* variables
        while IFS= read -r line; do
            # Skip comments and empty lines
            [[ "$line" =~ ^#.*$ ]] && continue
            [[ -z "$line" ]] && continue
            
            # Only process ZEBRA_, CLOUDFLARE_, and NGROK_ variables
            if [[ "$line" =~ ^(ZEBRA_|CLOUDFLARE_|NGROK_) ]]; then
                export "$line"
                echo -e "${CYAN}  ✓ $line${NC}"
            fi
        done < "$env_file"
    elif [[ -n "$ENV_FILE_PATH" ]]; then
        echo -e "${YELLOW}⚠️ Environment file not found: $env_file${NC}"
    fi
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

build_docker_env_args() {
    local env_args=""
    
    # Base environment variables
    env_args+=" -e ZEBRA_API_HOST=0.0.0.0"
    env_args+=" -e ZEBRA_API_PORT=5000"
    env_args+=" -e TZ=UTC"
    
    # Custom printer name
    local printer_name="${ZEBRA_PRINTER_NAME:-ZTC-ZD230-203dpi-ZPL}"
    env_args+=" -e ZEBRA_PRINTER_NAME=$printer_name"
    
    # Tunnel configuration
    if [[ -n "$DOMAIN" ]]; then
        env_args+=" -e ZEBRA_DOMAIN=$DOMAIN"
    elif [[ -n "$ZEBRA_DOMAIN" ]]; then
        env_args+=" -e ZEBRA_DOMAIN=$ZEBRA_DOMAIN"
    fi
    
    if [[ -n "$TUNNEL_TYPE" ]]; then
        env_args+=" -e ZEBRA_TUNNEL_TYPE=$TUNNEL_TYPE"
    elif [[ -n "$ZEBRA_TUNNEL_TYPE" ]]; then
        env_args+=" -e ZEBRA_TUNNEL_TYPE=$ZEBRA_TUNNEL_TYPE"
    fi
    
    # Cloudflare token
    if [[ -n "$CLOUDFLARE_TOKEN" ]]; then
        env_args+=" -e CLOUDFLARE_TOKEN=$CLOUDFLARE_TOKEN"
    fi
    
    # Ngrok token
    if [[ -n "$NGROK_AUTHTOKEN" ]]; then
        env_args+=" -e NGROK_AUTHTOKEN=$NGROK_AUTHTOKEN"
    fi
    
    echo "$env_args"
}

pull_and_run() {
    echo -e "${BLUE}📥 Pulling latest image from Docker Hub...${NC}"
    docker pull $DOCKER_IMAGE
    
    echo -e "${BLUE}🚀 Starting Zebra Print Control System...${NC}"
    
    # Build environment arguments
    local env_args
    env_args=$(build_docker_env_args)
    
    # Show configuration if any tunnel settings are present
    if [[ -n "$ZEBRA_DOMAIN" || -n "$DOMAIN" || -n "$ZEBRA_TUNNEL_TYPE" || -n "$TUNNEL_TYPE" ]]; then
        echo -e "${CYAN}🔧 Configuration:${NC}"
        [[ -n "$ZEBRA_DOMAIN$DOMAIN" ]] && echo "  • Domain: ${ZEBRA_DOMAIN:-$DOMAIN}"
        [[ -n "$ZEBRA_TUNNEL_TYPE$TUNNEL_TYPE" ]] && echo "  • Tunnel: ${ZEBRA_TUNNEL_TYPE:-$TUNNEL_TYPE}"
    fi
    
    # Create network if it doesn't exist (same as docker-compose)
    if ! docker network ls | grep -q zebra-print-network; then
        echo -e "${BLUE}🌐 Creating zebra-print-network...${NC}"
        docker network create zebra-print-network
    fi
    
    # Run container with environment variables and proper network
    eval "docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        --privileged \
        --pull always \
        --network zebra-print-network \
        --device=/dev/bus/usb:/dev/bus/usb \
        -p 5000:5000 \
        -p 8631:631 \
        -v zebra_data:/app/data \
        -v zebra_logs:/var/log/zebra-print \
        -v /dev:/dev:ro \
        $env_args \
        $DOCKER_IMAGE"
}

run_interactive_setup() {
    echo -e "${BLUE}🔧 Starting interactive setup...${NC}"
    echo -e "${YELLOW}💡 Accessing container control panel...${NC}"
    
    # Wait a moment for container to be ready
    sleep 3
    
    # Run the interactive setup
    docker exec -it $CONTAINER_NAME python3 zebra_control_v2.py
}

start_tunnel() {
    local domain="${ZEBRA_DOMAIN:-$DOMAIN}"
    local tunnel_type="${ZEBRA_TUNNEL_TYPE:-$TUNNEL_TYPE}"
    
    if [[ -z "$domain" || -z "$tunnel_type" ]]; then
        return 0  # No tunnel configuration
    fi
    
    echo -e "${BLUE}🚀 Starting $tunnel_type tunnel for $domain...${NC}"
    
    if [[ "$tunnel_type" == "cloudflare" && -n "$CLOUDFLARE_TOKEN" ]]; then
        # Start Cloudflare tunnel
        docker exec -d $CONTAINER_NAME bash -c "cloudflared tunnel --url http://127.0.0.1:5000 run --token $CLOUDFLARE_TOKEN > /var/log/cloudflare.log 2>&1"
        
        # Wait for tunnel to establish
        echo -e "${YELLOW}⏳ Establishing tunnel connections...${NC}"
        sleep 8
        
        # Check if tunnel process is running
        if docker exec $CONTAINER_NAME bash -c "ps aux | grep -q '[c]loudflared'"; then
            echo -e "${GREEN}✅ Cloudflare tunnel started${NC}"
            return 0
        else
            echo -e "${RED}❌ Cloudflare tunnel failed to start${NC}"
            return 1
        fi
        
    elif [[ "$tunnel_type" == "ngrok" && -n "$NGROK_AUTHTOKEN" ]]; then
        # Start Ngrok tunnel
        docker exec -d $CONTAINER_NAME bash -c "ngrok http 5000 --authtoken=$NGROK_AUTHTOKEN > /var/log/ngrok.log 2>&1"
        
        echo -e "${YELLOW}⏳ Starting ngrok tunnel...${NC}"
        sleep 5
        
        if docker exec $CONTAINER_NAME bash -c "ps aux | grep -q '[n]grok'"; then
            echo -e "${GREEN}✅ Ngrok tunnel started${NC}"
            return 0
        else
            echo -e "${RED}❌ Ngrok tunnel failed to start${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️ Tunnel configuration incomplete${NC}"
        echo "  • Type: $tunnel_type"
        echo "  • Token: $([ -n "$CLOUDFLARE_TOKEN$NGROK_AUTHTOKEN" ] && echo "Present" || echo "Missing")"
        return 1
    fi
}

verify_tunnel() {
    local domain="${ZEBRA_DOMAIN:-$DOMAIN}"
    
    if [[ -z "$domain" ]]; then
        return 0  # No tunnel to verify
    fi
    
    echo -e "${BLUE}🔍 Verifying tunnel connectivity...${NC}"
    
    # Try to reach the health endpoint
    local max_attempts=3
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "https://$domain/health" &> /dev/null; then
            echo -e "${GREEN}✅ Tunnel is working: https://$domain${NC}"
            echo -e "${CYAN}🌐 Webhook URL: https://$domain/print${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Attempt $attempt/$max_attempts...${NC}"
        sleep 5
        ((attempt++))
    done
    
    echo -e "${RED}❌ Tunnel verification failed${NC}"
    echo -e "${YELLOW}💡 Common fixes:${NC}"
    echo "  1. Check Cloudflare dashboard tunnel configuration"
    echo "  2. Ensure domain points to: http://localhost:5000"
    echo "  3. Verify tunnel token is correct"
    echo "  4. Check logs: docker logs $CONTAINER_NAME"
    return 1
}

show_status() {
    echo -e "${GREEN}✅ System started successfully!${NC}"
    echo
    echo -e "${CYAN}🌐 Services available at:${NC}"
    echo "  • API Server:    http://localhost:5000"
    echo "  • Health Check:  http://localhost:5000/health"
    echo "  • CUPS Admin:    http://localhost:8631"
    echo
    
    # Wait a moment for container to start
    sleep 3
    
    # Quick health check
    if curl -f http://localhost:5000/health &> /dev/null; then
        echo -e "${GREEN}✅ Local API is responding${NC}"
    else
        echo -e "${YELLOW}⏳ API starting up... (check logs if it doesn't respond in 30s)${NC}"
        return 1
    fi
    
    # Auto-start and verify tunnel if configured
    local domain="${ZEBRA_DOMAIN:-$DOMAIN}"
    if [[ -n "$domain" ]]; then
        echo
        if start_tunnel && verify_tunnel; then
            echo
            echo -e "${GREEN}🎉 System fully operational!${NC}"
            echo -e "${CYAN}📍 Tunnel Access: https://$domain${NC}"
        else
            echo
            echo -e "${YELLOW}⚠️ Local system working, tunnel needs attention${NC}"
        fi
    fi
    
    echo
    echo -e "${YELLOW}💡 Useful commands:${NC}"
    echo "  • Check status:  docker ps"
    echo "  • View logs:     docker logs $CONTAINER_NAME"
    echo "  • Access shell:  docker exec -it $CONTAINER_NAME /bin/bash"
    echo "  • Stop system:   docker stop $CONTAINER_NAME"
}

create_sample_env_file() {
    if [[ ! -f "$ENV_FILE" ]]; then
        echo -e "${BLUE}📝 Creating sample .env file...${NC}"
        cat > "$ENV_FILE" << EOF
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
EOF
        echo -e "${GREEN}✅ Sample .env file created. Edit it with your configuration.${NC}"
    fi
}

# Main execution
parse_arguments "$@"
print_banner
load_env_file
check_requirements
check_usb_printer
stop_existing
pull_and_run
show_status

# Create sample .env if it doesn't exist
create_sample_env_file

# Run interactive setup if requested
if [[ "$SETUP_MODE" == "true" ]]; then
    run_interactive_setup
fi