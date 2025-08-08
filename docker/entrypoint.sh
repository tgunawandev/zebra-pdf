#!/bin/bash

echo "🚀 Starting Zebra Print Control System (Docker)"
echo "================================================"

# Start CUPS service
echo "📱 Starting CUPS printer service..."
service cups start

# Wait for CUPS to be ready
sleep 2

# Detect and configure Zebra printers
echo "🔍 Detecting Zebra printers..."
/usr/local/bin/detect-printer.sh

# Initialize database
echo "🗄️  Initializing database..."
cd /app
python3 -c "
from zebra_print.database.db_manager import DatabaseManager
db = DatabaseManager('/app/data/zebra_print.db')
print('✅ Database initialized')
"

# Set proper permissions
chown -R root:root /app/data
chmod 755 /app/data

echo "✅ Zebra Print Control System ready!"
echo "🌐 API will be available on port 5000"
echo "🖨️  CUPS admin available on port 631"

# Execute the main command
exec "$@"