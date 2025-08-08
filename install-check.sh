#!/bin/bash

# Zebra Print Control System - Installation Verification
# Checks user computer and guides through setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║      🔍 ZEBRA PRINT INSTALLATION CHECK       ║${NC}"
    echo -e "${PURPLE}║         Verifying User Computer Setup        ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════╝${NC}"
    echo
}

check_status=0
total_checks=0

print_check() {
    local status=$1
    local message=$2
    local details=$3
    
    total_checks=$((total_checks + 1))
    
    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✅ $message${NC}"
        [ -n "$details" ] && echo -e "   ${CYAN}$details${NC}"
        check_status=$((check_status + 1))
    elif [ "$status" = "warn" ]; then
        echo -e "${YELLOW}⚠️ $message${NC}"
        [ -n "$details" ] && echo -e "   ${YELLOW}$details${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
        [ -n "$details" ] && echo -e "   ${RED}$details${NC}"
    fi
}

print_banner

echo -e "${BLUE}🔍 Checking installation requirements...${NC}"
echo

# 1. Check Docker installation
echo -e "${CYAN}1. Docker Requirements:${NC}"
if command -v docker &> /dev/null; then
    docker_version=$(docker --version 2>/dev/null | cut -d' ' -f3 | cut -d',' -f1)
    print_check "pass" "Docker installed" "Version: $docker_version"
    
    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        print_check "pass" "Docker daemon running"
        
        # Check Docker permissions
        if docker ps &> /dev/null; then
            print_check "pass" "Docker permissions OK"
        else
            print_check "fail" "Docker permission denied" "Run: sudo usermod -aG docker \$USER && newgrp docker"
        fi
    else
        print_check "fail" "Docker daemon not running" "Start Docker service or Docker Desktop"
    fi
    
    # Check Docker Compose
    if docker compose version &> /dev/null; then
        compose_version=$(docker compose version 2>/dev/null | head -1 | cut -d' ' -f4)
        print_check "pass" "Docker Compose available" "Version: $compose_version"
    else
        print_check "fail" "Docker Compose not available" "Install Docker with Compose plugin"
    fi
else
    print_check "fail" "Docker not installed" "Install from: https://docs.docker.com/get-docker/"
fi

echo

# 2. Check USB access for printer
echo -e "${CYAN}2. USB Printer Access:${NC}"
if command -v lsusb &> /dev/null; then
    zebra_devices=$(lsusb 2>/dev/null | grep -i zebra || true)
    if [ -n "$zebra_devices" ]; then
        print_check "pass" "Zebra printer detected" "$zebra_devices"
    else
        print_check "warn" "No Zebra printer detected" "Connect printer and run check again"
    fi
    
    # Check USB permissions
    if [ -r /dev/bus/usb ] && [ -w /dev/bus/usb ]; then
        print_check "pass" "USB device access OK"
    else
        print_check "warn" "USB permissions may need adjustment" "Docker will run with --privileged for USB access"
    fi
else
    print_check "warn" "lsusb not available" "Install usbutils package if needed"
fi

echo

# 3. Check network ports
echo -e "${CYAN}3. Network Port Availability:${NC}"
if command -v netstat &> /dev/null || command -v ss &> /dev/null; then
    # Check port 5000 (API)
    if netstat -tln 2>/dev/null | grep -q ":5000 " || ss -tln 2>/dev/null | grep -q ":5000 "; then
        print_check "warn" "Port 5000 in use" "System will try to use this port anyway"
    else
        print_check "pass" "Port 5000 available"
    fi
    
    # Check port 8631 (CUPS)
    if netstat -tln 2>/dev/null | grep -q ":8631 " || ss -tln 2>/dev/null | grep -q ":8631 "; then
        print_check "warn" "Port 8631 in use" "CUPS may conflict"
    else
        print_check "pass" "Port 8631 available"
    fi
    
    # Check port 631 (system CUPS)
    if netstat -tln 2>/dev/null | grep -q ":631 " || ss -tln 2>/dev/null | grep -q ":631 "; then
        print_check "pass" "Port 631 in use (system CUPS)" "We use port 8631 to avoid conflict"
    else
        print_check "pass" "Port 631 available"
    fi
else
    print_check "warn" "Cannot check port status" "netstat/ss not available"
fi

echo

# 4. Check required files
echo -e "${CYAN}4. System Files:${NC}"
required_files=("docker-compose.yml" "Dockerfile.alpine" "zebra.sh" "cloudflare-auth.sh")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_check "pass" "Found $file"
    else
        print_check "fail" "Missing $file" "Ensure you're in the correct directory"
    fi
done

# Check executable permissions
if [ -x "zebra.sh" ]; then
    print_check "pass" "zebra.sh executable"
else
    print_check "warn" "zebra.sh not executable" "Run: chmod +x zebra.sh"
fi

if [ -x "cloudflare-auth.sh" ]; then
    print_check "pass" "cloudflare-auth.sh executable"
else
    print_check "warn" "cloudflare-auth.sh not executable" "Run: chmod +x cloudflare-auth.sh"
fi

echo

# 5. System resources
echo -e "${CYAN}5. System Resources:${NC}"
# Check available disk space
available_space=$(df . | tail -1 | awk '{print $4}')
if [ "$available_space" -gt 1048576 ]; then  # 1GB in KB
    available_gb=$((available_space / 1048576))
    print_check "pass" "Disk space sufficient" "${available_gb}GB available"
else
    available_mb=$((available_space / 1024))
    print_check "warn" "Low disk space" "${available_mb}MB available (1GB+ recommended)"
fi

# Check memory
if command -v free &> /dev/null; then
    available_mem=$(free -m | awk '/^Mem:/{print $7}')
    if [ "$available_mem" -gt 512 ]; then
        print_check "pass" "Memory sufficient" "${available_mem}MB available"
    else
        print_check "warn" "Low memory" "${available_mem}MB available (512MB+ recommended)"
    fi
fi

echo
echo -e "${BLUE}📊 Installation Check Summary:${NC}"
echo "============================================"

percentage=$((check_status * 100 / total_checks))
if [ $percentage -ge 80 ]; then
    echo -e "${GREEN}✅ Ready for installation! ($check_status/$total_checks checks passed - $percentage%)${NC}"
    echo ""
    echo -e "${YELLOW}🚀 Next steps:${NC}"
    echo "1. Run: ./zebra.sh start      # Auto-configures printer"
    echo "2. Run: ./zebra.sh auth       # Setup Cloudflare (one-time)"
    echo "3. Run: ./zebra.sh setup      # Configure domain & tunnel"
    echo "4. Test printing with your domain URL"
    echo ""
elif [ $percentage -ge 60 ]; then
    echo -e "${YELLOW}⚠️ Installation possible with warnings ($check_status/$total_checks checks passed - $percentage%)${NC}"
    echo ""
    echo -e "${YELLOW}💡 Recommended fixes:${NC}"
    echo "• Address warnings above before proceeding"
    echo "• System should still work but may have issues"
    echo ""
else
    echo -e "${RED}❌ Installation not recommended ($check_status/$total_checks checks passed - $percentage%)${NC}"
    echo ""
    echo -e "${RED}🔧 Required fixes:${NC}"
    echo "• Fix critical issues marked with ❌ above"
    echo "• Re-run this check after fixing issues"
    echo ""
fi

echo -e "${CYAN}💡 For detailed setup guide: see QUICK_CLOUDFLARE_SETUP.md${NC}"
echo -e "${CYAN}🔍 For troubleshooting: see docs/AUTO_SETUP_GUIDE.md${NC}"