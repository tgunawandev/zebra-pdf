#!/bin/bash

echo "🚀 Starting Zebra Print Control System (Alpine)"
echo "==============================================="

# Start CUPS service (Alpine) - handled by supervisor
echo "📱 CUPS will be started by supervisor..."

# Detect USB printers (simplified for Alpine)
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
echo "🌐 API will be available on port 5000"

# Execute the main command
exec "$@"