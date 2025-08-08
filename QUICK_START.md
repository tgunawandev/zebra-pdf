# 🦓 Zebra Print Control System - Enhanced Quick Start

Run the Zebra Print Control System instantly without downloading the repository, with full support for tunnel configuration and interactive setup.

## 🚀 One-Command Installation

### Simple Installation
```bash
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.sh | bash
```

### With Interactive Setup
```bash
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.sh | bash -s -- --setup
```

### Windows (Command Prompt)
```cmd
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.bat -o zebra-run.bat && zebra-run.bat
```

### Windows (PowerShell)
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.ps1" -OutFile "zebra-run.ps1"; .\zebra-run.ps1
```

## 🔧 Advanced Usage Options

### Command Line Options
```bash
# Download and run the script first
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.sh -o zebra-run.sh
chmod +x zebra-run.sh

# Basic usage
./zebra-run.sh

# With interactive setup (recommended for first-time users)
./zebra-run.sh --setup

# Quick domain setup
./zebra-run.sh --domain tln-zebra-01.abcfood.app --tunnel cloudflare

# Using custom environment file
./zebra-run.sh --env-file my-config.env

# Show all options
./zebra-run.sh --help
```

### Environment Variables
Set these before running the script:
```bash
export ZEBRA_DOMAIN=tln-zebra-01.abcfood.app
export ZEBRA_TUNNEL_TYPE=cloudflare
export CLOUDFLARE_TOKEN=your_token_here
./zebra-run.sh
```

### Using .env File (Recommended)
Create a `.env` file in your directory:
```env
# Zebra Print Control System Configuration
ZEBRA_DOMAIN=tln-zebra-01.abcfood.app
ZEBRA_TUNNEL_TYPE=cloudflare
CLOUDFLARE_TOKEN=your_cloudflare_tunnel_token_here

# Optional: Custom printer name
ZEBRA_PRINTER_NAME=ZTC-ZD230-203dpi-ZPL
```

Then run:
```bash
./zebra-run.sh  # Automatically loads .env
```

## 🌐 Tunnel Configuration

### Supported Tunnel Types
- **Cloudflare Tunnel** (recommended for production)
- **Ngrok** (great for testing)

### Cloudflare Tunnel Setup
1. Create a `.env` file:
   ```env
   ZEBRA_DOMAIN=your-domain.example.com
   ZEBRA_TUNNEL_TYPE=cloudflare
   CLOUDFLARE_TOKEN=your_tunnel_token
   ```

2. Run with the configuration:
   ```bash
   ./zebra-run.sh
   ```

### Ngrok Tunnel Setup  
1. Create a `.env` file:
   ```env
   ZEBRA_TUNNEL_TYPE=ngrok
   NGROK_AUTHTOKEN=your_ngrok_token
   ```

2. Run the system:
   ```bash
   ./zebra-run.sh
   ```

## 📋 Manual Docker Run

For advanced users who prefer direct Docker commands:

```bash
docker run -d \
  --name zebra-print-control \
  --restart unless-stopped \
  --privileged \
  --device=/dev/bus/usb:/dev/bus/usb \
  -p 5000:5000 \
  -p 8631:631 \
  -v zebra_data:/app/data \
  -v zebra_logs:/var/log/zebra-print \
  -e ZEBRA_API_HOST=0.0.0.0 \
  -e ZEBRA_DOMAIN=your-domain.com \
  -e ZEBRA_TUNNEL_TYPE=cloudflare \
  -e CLOUDFLARE_TOKEN=your_token \
  kodemeio/zebra-pdf:latest
```

## 📝 Requirements

- ✅ Docker installed and running
- ✅ USB Zebra printer connected (optional)
- ✅ Ports 5000 and 8631 available
- ✅ Internet connection for tunnel setup

## 🌐 After Installation

**Local Services:**
- 🖥️ API Server: http://localhost:5000
- 🩺 Health Check: http://localhost:5000/health  
- 🖨️ CUPS Admin: http://localhost:8631

**Tunnel Services (if configured):**
- 🌍 Public API: https://your-domain.com
- 🔗 Webhook URL: https://your-domain.com/print

## 🛠️ Useful Commands

```bash
# Check container status
docker ps

# View system logs
docker logs zebra-print-control

# Access interactive setup anytime
docker exec -it zebra-print-control python3 zebra_control_v2.py

# Access container shell
docker exec -it zebra-print-control /bin/bash

# Stop system
docker stop zebra-print-control

# Restart system (pulls latest updates)
./zebra-run.sh

# Remove system completely
docker stop zebra-print-control && docker rm zebra-print-control
```

## 🖨️ API Usage

### Test Print API
```bash
curl -X POST http://localhost:5000/print \
  -H "Content-Type: application/json" \
  -d '{
    "labels": [{
      "qr_code": "01010101160",
      "do_number": "W-CPN/OUT/00002",
      "route": "Route A",
      "date": "12/04/22",
      "customer": "Customer Name",
      "so_number": "SO-67890",
      "mo_number": "MO-12345",
      "item": "Product Name",
      "qty": "100",
      "uom": "PCS"
    }]
  }'
```

### With Tunnel (External Access)
```bash
curl -X POST https://your-domain.com/print \
  -H "Content-Type: application/json" \
  -d '{ ... }'  # Same JSON as above
```

## 🔄 Updating

To get the latest version:
```bash
# Re-run the script - it always pulls the latest image
./zebra-run.sh
```

The system automatically:
- ✅ Pulls the latest Docker image
- ✅ Stops old containers
- ✅ Preserves your configuration
- ✅ Maintains data volumes

## 🚨 Troubleshooting

### Container Not Starting
```bash
# Check logs
docker logs zebra-print-control

# Verify ports are available
netstat -tulpn | grep -E ':(5000|8631)'
```

### Tunnel Issues
```bash
# Access interactive setup
docker exec -it zebra-print-control python3 zebra_control_v2.py

# Check tunnel status in logs
docker logs zebra-print-control | grep -i tunnel
```

### Printer Not Detected
```bash
# Check USB devices
lsusb | grep -i zebra

# Restart with printer connected
docker restart zebra-print-control
```

## 👩‍💻 For Developers

If you want to modify the source code:
```bash
git clone https://github.com/tgunawandev/zebra-pdf.git
cd zebra-pdf
./zebra.sh start
```

---

## 🎯 Quick Examples

**Simple setup:**
```bash
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.sh | bash
```

**Production setup with Cloudflare:**
```bash
# Create .env file with your settings
echo "ZEBRA_DOMAIN=print.yourcompany.com" > .env
echo "ZEBRA_TUNNEL_TYPE=cloudflare" >> .env
echo "CLOUDFLARE_TOKEN=your_token" >> .env

# Run with setup
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.sh | bash -s -- --setup
```

**Quick test setup:**
```bash
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.sh | bash -s -- --tunnel ngrok
```