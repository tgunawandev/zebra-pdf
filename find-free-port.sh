#!/bin/bash

# Port Conflict Resolution Script
# Finds available ports and updates system configuration

find_free_port() {
    local start_port=$1
    local max_port=${2:-$((start_port + 100))}
    
    for port in $(seq $start_port $max_port); do
        if ! netstat -tln 2>/dev/null | grep -q ":$port " && ! ss -tln 2>/dev/null | grep -q ":$port "; then
            echo $port
            return 0
        fi
    done
    
    echo ""
    return 1
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🔍 Port Conflict Resolution${NC}"
echo "==========================="

# Check primary ports
API_PORT=5000
CUPS_PORT=8631

echo -e "${CYAN}Checking port availability:${NC}"

# Check API port (5000)
if netstat -tln 2>/dev/null | grep -q ":$API_PORT " || ss -tln 2>/dev/null | grep -q ":$API_PORT "; then
    echo -e "${RED}❌ Port $API_PORT (API) is in use${NC}"
    
    # Find alternative port
    NEW_API_PORT=$(find_free_port 5001)
    if [ -n "$NEW_API_PORT" ]; then
        echo -e "${GREEN}✅ Found alternative: Port $NEW_API_PORT${NC}"
        
        # Update docker-compose.yml
        if [ -f "docker-compose.yml" ]; then
            sed -i.backup "s/\"5000:5000\"/\"$NEW_API_PORT:5000\"/" docker-compose.yml
            echo -e "${YELLOW}🔧 Updated docker-compose.yml: $API_PORT → $NEW_API_PORT${NC}"
        fi
        
        # Update scripts
        find . -name "*.sh" -exec sed -i.backup "s/localhost:5000/localhost:$NEW_API_PORT/g" {} \;
        find . -name "*.bat" -exec sed -i.backup "s/localhost:5000/localhost:$NEW_API_PORT/g" {} \;
        find . -name "*.ps1" -exec sed -i.backup "s/localhost:5000/localhost:$NEW_API_PORT/g" {} \;
        
        echo -e "${GREEN}✅ Updated all scripts to use port $NEW_API_PORT${NC}"
        API_PORT=$NEW_API_PORT
    else
        echo -e "${RED}❌ No available ports found in range 5001-5100${NC}"
    fi
else
    echo -e "${GREEN}✅ Port $API_PORT (API) is available${NC}"
fi

# Check CUPS port (8631)
if netstat -tln 2>/dev/null | grep -q ":$CUPS_PORT " || ss -tln 2>/dev/null | grep -q ":$CUPS_PORT "; then
    echo -e "${RED}❌ Port $CUPS_PORT (CUPS) is in use${NC}"
    
    # Find alternative port
    NEW_CUPS_PORT=$(find_free_port 8632)
    if [ -n "$NEW_CUPS_PORT" ]; then
        echo -e "${GREEN}✅ Found alternative: Port $NEW_CUPS_PORT${NC}"
        
        # Update docker-compose.yml
        if [ -f "docker-compose.yml" ]; then
            sed -i.backup "s/\"$CUPS_PORT:631\"/\"$NEW_CUPS_PORT:631\"/" docker-compose.yml
            echo -e "${YELLOW}🔧 Updated docker-compose.yml: $CUPS_PORT → $NEW_CUPS_PORT${NC}"
        fi
        
        # Update scripts
        find . -name "*.sh" -exec sed -i.backup "s/localhost:$CUPS_PORT/localhost:$NEW_CUPS_PORT/g" {} \;
        find . -name "*.bat" -exec sed -i.backup "s/localhost:$CUPS_PORT/localhost:$NEW_CUPS_PORT/g" {} \;
        find . -name "*.ps1" -exec sed -i.backup "s/localhost:$CUPS_PORT/localhost:$NEW_CUPS_PORT/g" {} \;
        
        echo -e "${GREEN}✅ Updated all scripts to use port $NEW_CUPS_PORT${NC}"
        CUPS_PORT=$NEW_CUPS_PORT
    else
        echo -e "${RED}❌ No available ports found in range 8632-8731${NC}"
    fi
else
    echo -e "${GREEN}✅ Port $CUPS_PORT (CUPS) is available${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}📊 Final Configuration:${NC}"
echo "  • API Server:  http://localhost:$API_PORT"
echo "  • CUPS Admin:  http://localhost:$CUPS_PORT"
echo ""

# Save configuration
cat > .port-config << EOF
API_PORT=$API_PORT
CUPS_PORT=$CUPS_PORT
LAST_CHECK=$(date)
EOF

echo -e "${GREEN}✅ Port configuration saved to .port-config${NC}"
echo -e "${YELLOW}💡 Run './zebra.sh start' to apply changes${NC}"