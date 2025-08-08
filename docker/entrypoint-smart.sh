#!/bin/bash

# Smart entrypoint with dynamic port detection

echo "🚀 Starting Zebra Print Control System (Smart Mode)"
echo "=================================================="

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
    
    echo $start_port  # fallback to original
    return 1
}

# Check if default API port is available
API_PORT=${ZEBRA_API_PORT:-5000}
if netstat -tln 2>/dev/null | grep -q ":$API_PORT " || ss -tln 2>/dev/null | grep -q ":$API_PORT "; then
    echo "⚠️ Port $API_PORT is in use, finding alternative..."
    NEW_API_PORT=$(find_free_port $((API_PORT + 1)))
    if [ "$NEW_API_PORT" != "$API_PORT" ]; then
        echo "✅ Using port $NEW_API_PORT instead"
        export ZEBRA_API_PORT=$NEW_API_PORT
        
        # Update supervisor config with new port
        sed -i "s/ZEBRA_API_PORT=5000/ZEBRA_API_PORT=$NEW_API_PORT/" /etc/supervisor/conf.d/zebra-print.conf
        
        # Create port mapping file for external access
        echo "API_PORT=$NEW_API_PORT" > /app/data/current-ports.conf
        echo "CUPS_PORT=631" >> /app/data/current-ports.conf
    fi
fi

# Start CUPS service - handled by supervisor
echo "📱 CUPS will be started by supervisor..."

# Detect USB printers
echo "🔍 Detecting USB Zebra printers..."
if command -v lsusb &> /dev/null; then
    USB_DEVICES=$(lsusb 2>/dev/null | grep -i zebra || true)
    if [ -n "$USB_DEVICES" ]; then
        echo "✅ Found Zebra USB device(s):"
        echo "$USB_DEVICES"
    else
        echo "⚠️ No Zebra USB printers detected"
    fi
else
    echo "ℹ️ lsusb not available, skipping USB detection"
fi

# Initialize database
echo "🗄️ Initializing database..."
cd /app
python3 -c "
from zebra_print.database.db_manager import DatabaseManager
db = DatabaseManager('/app/data/zebra_print.db')
print('✅ Database initialized')
" || echo "⚠️ Database initialization failed"

# Auto-configure printers (run in background after supervisor starts)
echo "🤖 Setting up automatic printer configuration..."
nohup bash -c 'sleep 10 && /app/docker/auto-printer-setup.sh' > /var/log/zebra-print/auto-setup.log 2>&1 &

# Set permissions
chown -R root:root /app/data 2>/dev/null || true
chmod 755 /app/data 2>/dev/null || true

echo "✅ Zebra Print Control System ready!"
echo "🌐 API will be available on port ${ZEBRA_API_PORT:-5000}"

# Execute the main command
exec "$@"