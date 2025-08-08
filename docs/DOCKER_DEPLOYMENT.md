# 🐳 Docker Deployment Guide

## ✨ **Complete Production-Ready Solution**

This Docker setup provides:
- ✅ **USB Zebra Printer Auto-Detection**
- ✅ **SQLite Persistent Configuration**
- ✅ **Custom Domain Mapping** (e.g., `tln-zebra-01.abcfood.app`)
- ✅ **CUPS Printer Management**
- ✅ **Cloudflare & Ngrok Tunnels**
- ✅ **Easy Deployment Anywhere**

---

## 🚀 **Quick Start**

### **Option 1: Docker Compose (Recommended)**
```bash
# Clone and build
git clone <your-repo>
cd zebra-pdf

# Start with USB printer access
docker-compose up -d

# Check logs
docker-compose logs -f
```

### **Option 2: Docker Run**
```bash
# Build image
docker build -t zebra-print .

# Run with USB printer access
docker run -d \
  --name zebra-print \
  --privileged \
  --device=/dev/bus/usb \
  -p 5000:5000 \
  -p 8631:631 \
  -v zebra_data:/app/data \
  zebra-print
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
ZEBRA_API_HOST=0.0.0.0          # API host
ZEBRA_API_PORT=5000             # API port
ZEBRA_PRINTER_NAME=ZTC-ZD230-203dpi-ZPL  # Printer name
ZEBRA_DB_PATH=/app/data/zebra_print.db   # Database path
```

### **Custom Domain Setup**
1. **Access Container**:
   ```bash
   docker exec -it zebra-print bash
   ```

2. **Set Custom Domain**:
   ```bash
   python3 -c "
   from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
   tunnel = CloudflareNamedTunnel()
   tunnel.set_custom_domain('tln-zebra-01.abcfood.app')
   "
   ```

3. **Setup Named Tunnel**:
   ```bash
   # Authenticate (one-time setup)
   cloudflared tunnel login
   
   # Setup will create tunnel and DNS records
   python3 zebra_control_v2.py
   # Select option 4: Setup Tunnel
   # Select option 1: Cloudflare
   ```

---

## 📱 **Accessing Services**

| Service | URL | Purpose |
|---------|-----|---------|
| **API Server** | `http://localhost:5000` | Label printing API |
| **Health Check** | `http://localhost:5000/health` | Service health |
| **CUPS Admin** | `http://localhost:8631` | Printer management |
| **Control Panel** | `docker exec -it zebra-print python3 zebra_control_v2.py` | Interactive CLI |

---

## 🖨️ **Printer Detection**

The system automatically detects USB Zebra printers:

1. **Auto-Detection**: Scans USB devices on startup
2. **CUPS Configuration**: Automatically configures printer
3. **Database Storage**: Saves printer config to SQLite
4. **Test Print**: Performs connection test

### **Manual Printer Setup**
If auto-detection fails:
```bash
# Access container
docker exec -it zebra-print bash

# List USB devices
lsusb | grep -i zebra

# Check printer devices
lpinfo -v

# Manual printer configuration
python3 zebra_control_v2.py
# Select option 7: Printer Management
```

---

## 🌐 **Tunnel Configuration**

### **Cloudflare Named Tunnels (Recommended)**
```bash
# 1. Set your custom domain
python3 -c "
from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
tunnel = CloudflareNamedTunnel()
success, msg = tunnel.set_custom_domain('your-subdomain.yourdomain.com')
print(msg)
"

# 2. Authenticate with Cloudflare (one-time)
cloudflared tunnel login

# 3. Setup and start tunnel
python3 zebra_control_v2.py
# Option 4: Setup Tunnel → Cloudflare
# Option 5: Start Tunnel → Cloudflare
```

**Result**: Permanent URL like `https://tln-zebra-01.abcfood.app/print`

### **Quick Tunnels (Development)**
For temporary URLs without domain setup:
```bash
# Uses cloudflared quick tunnels or ngrok
python3 zebra_control_v2.py
# Option 5: Start Tunnel → Ngrok or Cloudflare Quick
```

---

## 💾 **Data Persistence**

### **Volumes**
- `zebra_data:/app/data` - SQLite database and configurations
- `zebra_logs:/var/log/zebra-print` - Application logs

### **Database Location**
- **Path**: `/app/data/zebra_print.db`
- **Tables**: `tunnel_configs`, `system_state`, `printer_configs`

### **Backup Data**
```bash
# Backup database
docker cp zebra-print:/app/data/zebra_print.db ./backup.db

# Restore database
docker cp ./backup.db zebra-print:/app/data/zebra_print.db
```

---

## 🔍 **Troubleshooting**

### **Printer Not Detected**
```bash
# Check USB devices
docker exec -it zebra-print lsusb

# Check printer devices
docker exec -it zebra-print lpinfo -v

# Check CUPS status
docker exec -it zebra-print service cups status
```

### **Tunnel Issues**
```bash
# Check tunnel status
docker exec -it zebra-print python3 -c "
from zebra_print.database.db_manager import DatabaseManager
db = DatabaseManager('/app/data/zebra_print.db')
configs = db.get_all_tunnel_configs()
for c in configs:
    print(f'{c.name}: configured={c.is_configured}, active={c.is_active}')
"

# Reset tunnel configuration
docker exec -it zebra-print rm -f /app/data/zebra_print.db
docker restart zebra-print
```

### **View Logs**
```bash
# Container logs
docker logs zebra-print

# Service logs
docker exec -it zebra-print tail -f /var/log/zebra-print/api.log
docker exec -it zebra-print tail -f /var/log/zebra-print/cups.log
```

---

## 🏭 **Production Deployment**

### **Docker Swarm**
```yaml
version: '3.8'
services:
  zebra-print:
    image: zebra-print:latest
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.has-zebra-printer == true
    networks:
      - zebra-network
```

### **Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zebra-print
spec:
  template:
    spec:
      containers:
      - name: zebra-print
        image: zebra-print:latest
        securityContext:
          privileged: true
        volumeMounts:
        - name: dev-usb
          mountPath: /dev/bus/usb
      volumes:
      - name: dev-usb
        hostPath:
          path: /dev/bus/usb
```

---

## ✅ **Verification Checklist**

After deployment:
- [ ] Container starts successfully
- [ ] API responds on port 5000
- [ ] CUPS accessible on port 8631
- [ ] USB printer detected and configured
- [ ] Database initialized
- [ ] Tunnel configured with custom domain
- [ ] Test print successful
- [ ] Webhook URL accessible from internet

---

## 📞 **Integration with Odoo**

1. **Get Webhook URL**:
   ```bash
   docker exec -it zebra-print python3 -c "
   from zebra_print.database.db_manager import DatabaseManager
   db = DatabaseManager('/app/data/zebra_print.db')
   config = db.get_tunnel_config('cloudflare_named')
   if config and config.domain_mapping:
       print(f'Webhook URL: https://{config.domain_mapping}/print')
   "
   ```

2. **Configure Odoo Webhook**: Use the URL from step 1

3. **Test Integration**: Send test label from Odoo

---

*🎉 **Your production-ready Zebra printing system is now containerized and ready for deployment anywhere!***