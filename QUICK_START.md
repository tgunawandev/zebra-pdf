# 🦓 Zebra Print Control System - Quick Start

Run the Zebra Print Control System instantly without downloading the repository.

## One-Command Installation

### Linux/Mac
```bash
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.sh | bash
```

### Windows (Command Prompt)
```cmd
curl -sSL https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.bat -o zebra-run.bat && zebra-run.bat
```

### Windows (PowerShell)
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/tgunawandev/zebra-pdf/master/zebra-run.ps1" -OutFile "zebra-run.ps1"; .\zebra-run.ps1
```

## Manual Docker Run

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
  -e ZEBRA_PRINTER_NAME=ZTC-ZD230-203dpi-ZPL \
  kodemeio/zebra-pdf:latest
```

## Requirements

- ✅ Docker installed and running
- ✅ USB Zebra printer connected (optional)
- ✅ Ports 5000 and 8631 available

## After Installation

🌐 **Services will be available at:**
- API Server: http://localhost:5000
- Health Check: http://localhost:5000/health  
- CUPS Admin: http://localhost:8631

## Useful Commands

```bash
# Check status
docker ps

# View logs
docker logs zebra-print-control

# Access container shell
docker exec -it zebra-print-control /bin/bash

# Stop system
docker stop zebra-print-control

# Remove system
docker stop zebra-print-control && docker rm zebra-print-control
```

## API Usage

Test the print API:
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

## For Developers

If you want to modify the source code, clone the repository:
```bash
git clone https://github.com/tgunawandev/zebra-pdf.git
cd zebra-pdf
./zebra.sh start
```