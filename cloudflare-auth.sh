#!/bin/bash

# Cloudflare Authentication Helper for Zebra Print Control
# This script handles Cloudflare authentication outside the container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🔐 Cloudflare Authentication Setup${NC}"
echo "=================================="

# Check if cloudflared is installed on host
if ! command -v cloudflared &> /dev/null; then
    echo -e "${YELLOW}📥 Installing cloudflared on host...${NC}"
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
        sudo dpkg -i cloudflared.deb
        rm cloudflared.deb
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install cloudflared
        else
            echo -e "${RED}❌ Please install Homebrew first or download cloudflared manually${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Unsupported OS. Please install cloudflared manually${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ cloudflared found${NC}"

# Check if already authenticated
if [ -f "$HOME/.cloudflared/cert.pem" ]; then
    echo -e "${GREEN}✅ Already authenticated with Cloudflare${NC}"
else
    echo -e "${YELLOW}🌐 Opening Cloudflare authentication...${NC}"
    echo "This will open your browser to authenticate with Cloudflare."
    echo "Please log in and authorize cloudflared."
    echo ""
    read -p "Press Enter to continue..."
    
    # Run authentication
    cloudflared tunnel login
    
    if [ -f "$HOME/.cloudflared/cert.pem" ]; then
        echo -e "${GREEN}✅ Authentication successful!${NC}"
    else
        echo -e "${RED}❌ Authentication failed${NC}"
        exit 1
    fi
fi

# Copy auth to container volume
echo -e "${BLUE}📋 Copying authentication to container...${NC}"

# Ensure container is running
if ! docker ps | grep -q zebra-print-control; then
    echo -e "${RED}❌ Container not running. Please run: ./zebra.sh start${NC}"
    exit 1
fi

# Copy .cloudflared directory to container
docker exec zebra-print-control mkdir -p /root/.cloudflared
docker cp "$HOME/.cloudflared/" zebra-print-control:/root/

echo -e "${GREEN}✅ Authentication copied to container${NC}"

# Test authentication in container
echo -e "${BLUE}🧪 Testing authentication in container...${NC}"
AUTH_TEST=$(docker exec zebra-print-control cloudflared tunnel list 2>&1)

if echo "$AUTH_TEST" | grep -q "NAME\|ID"; then
    echo -e "${GREEN}✅ Container authentication working${NC}"
    echo "Available tunnels:"
    echo "$AUTH_TEST" | sed 's/^/   /'
else
    echo -e "${RED}❌ Container authentication failed${NC}"
    echo "$AUTH_TEST"
    exit 1
fi

echo ""
echo -e "${CYAN}🎉 Cloudflare authentication setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run: ./zebra.sh setup"
echo "2. Choose option 4: Setup Tunnel"  
echo "3. Choose option 1: Cloudflare Named Tunnel"
echo "4. Your domain should work immediately"
echo ""