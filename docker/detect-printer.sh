#!/bin/bash

echo "🔍 Detecting USB Zebra printers..."

# Check for USB devices
USB_DEVICES=$(lsusb | grep -i zebra)

if [ -n "$USB_DEVICES" ]; then
    echo "✅ Found Zebra USB device(s):"
    echo "$USB_DEVICES"
    
    # Get device URI from lpinfo
    DEVICE_URI=$(lpinfo -v | grep usb | grep -i zebra | head -1 | awk '{print $2}')
    
    if [ -n "$DEVICE_URI" ]; then
        echo "📍 Device URI: $DEVICE_URI"
        
        # Configure printer in CUPS
        PRINTER_NAME="ZTC-ZD230-203dpi-ZPL"
        
        echo "🔧 Configuring printer: $PRINTER_NAME"
        
        # Remove existing printer if present
        lpadmin -x "$PRINTER_NAME" 2>/dev/null || true
        
        # Add new printer
        lpadmin -p "$PRINTER_NAME" \
                -v "$DEVICE_URI" \
                -P /dev/null \
                -o printer-is-accepting-jobs=true \
                -o printer-state=idle
        
        # Enable printer
        cupsenable "$PRINTER_NAME"
        cupsaccept "$PRINTER_NAME"
        
        # Set as default
        lpadmin -d "$PRINTER_NAME"
        
        echo "✅ Printer configured successfully: $PRINTER_NAME"
        
        # Test printer
        echo "🧪 Testing printer connection..."
        echo "^XA^HH^XZ" | lp -d "$PRINTER_NAME" -o raw && \
        echo "✅ Printer test successful" || \
        echo "⚠️  Printer test failed"
        
        # Save configuration to database
        python3 -c "
import sys
sys.path.append('/app')
from zebra_print.database.db_manager import DatabaseManager
from zebra_print.database.models import PrinterConfig
from datetime import datetime

db = DatabaseManager('/app/data/zebra_print.db')
config = PrinterConfig(
    name='$PRINTER_NAME',
    connection_type='USB',
    device_uri='$DEVICE_URI',
    is_default=True,
    is_configured=True,
    last_tested=datetime.now()
)
db.save_printer_config(config)
print('✅ Printer configuration saved to database')
"
        
    else
        echo "❌ Could not determine device URI"
    fi
else
    echo "⚠️  No Zebra USB printers detected"
    echo "📝 Available USB devices:"
    lsusb | head -10
    
    echo "📝 Available printer devices:"
    lpinfo -v | head -10
fi

echo "🔍 Printer detection completed"