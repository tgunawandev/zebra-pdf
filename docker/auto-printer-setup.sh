#!/bin/bash

echo "🖨️ Auto-configuring Zebra printers..."

# Wait for CUPS to be fully ready
sleep 3

# Detect USB Zebra printers
ZEBRA_DEVICES=$(lpinfo -v 2>/dev/null | grep -i "usb://.*zebra" || true)

if [ -z "$ZEBRA_DEVICES" ]; then
    echo "⚠️ No USB Zebra printers detected"
    echo "ℹ️ Connect printer and restart container if needed"
    exit 0
fi

echo "✅ Found Zebra printer(s):"
echo "$ZEBRA_DEVICES"

# Configure each detected printer
echo "$ZEBRA_DEVICES" | while IFS= read -r device_line; do
    if [ -n "$device_line" ]; then
        # Extract device URI
        DEVICE_URI=$(echo "$device_line" | awk '{print $2}')
        
        # Extract printer model name from URI
        PRINTER_MODEL=$(echo "$DEVICE_URI" | sed 's/.*\/\([^?]*\).*/\1/' | sed 's/%20/ /g')
        
        # Create printer name (remove spaces, make safe for CUPS)
        PRINTER_NAME=$(echo "$PRINTER_MODEL" | sed 's/ /-/g')
        
        echo "🔧 Configuring printer: $PRINTER_NAME"
        echo "   Device URI: $DEVICE_URI"
        
        # Check if printer already exists
        if lpstat -p "$PRINTER_NAME" &>/dev/null; then
            echo "ℹ️ Printer $PRINTER_NAME already configured"
        else
            # Configure printer with raw driver (best for ZPL)
            if lpadmin -p "$PRINTER_NAME" -E -v "$DEVICE_URI" -m raw 2>/dev/null; then
                echo "✅ Printer $PRINTER_NAME configured successfully"
                
                # Enable and accept jobs
                cupsenable "$PRINTER_NAME" 2>/dev/null || true
                cupsaccept "$PRINTER_NAME" 2>/dev/null || true
                
                # Set as default if it's the first/only printer
                PRINTER_COUNT=$(lpstat -p 2>/dev/null | wc -l)
                if [ "$PRINTER_COUNT" -eq 1 ]; then
                    lpadmin -d "$PRINTER_NAME" 2>/dev/null || true
                    echo "✅ Set as default printer"
                fi
            else
                echo "❌ Failed to configure printer $PRINTER_NAME"
            fi
        fi
    fi
done

# Show final printer status
echo "📋 Final printer configuration:"
lpstat -p 2>/dev/null | sed 's/^/   /' || echo "   No printers configured"

echo "✅ Auto-printer setup completed"