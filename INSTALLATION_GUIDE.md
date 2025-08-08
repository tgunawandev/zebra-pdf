# 💻 User Computer Installation Guide

## 🎯 **What Happens When Installing on User Computers**

This guide covers deploying the Zebra Print Control System on any user's computer with **automatic issue resolution**.

---

## ✅ **Issues Automatically Resolved**

### **1. Port Conflicts**
- **Problem**: User's system may have CUPS running on port 631
- **Auto-Fix**: System uses port 8631 instead (configured in docker-compose.yml)
- **Result**: ✅ No manual port configuration needed

### **2. Printer Configuration**  
- **Problem**: CUPS requires manual printer setup
- **Auto-Fix**: Auto-detects and configures Zebra printers on startup
- **Result**: ✅ Printer works immediately after start

### **3. Docker Setup Issues**
- **Problem**: Users may have wrong Docker versions or permissions
- **Auto-Fix**: Installation checker verifies and guides through fixes
- **Result**: ✅ Clear instructions for any missing components

### **4. Cloudflare Authentication**
- **Problem**: Browser authentication needed for tunnels
- **Auto-Fix**: Host-based authentication script handles browser flow
- **Result**: ✅ Simple `./zebra.sh auth` command

---

## 🚀 **User Installation Process**

### **Step 1: Pre-Installation Check**
```bash
# Download and check system
git clone <repository>
cd zebra-pdf

# Verify user computer is ready
./zebra.sh install
```

**Example output:**
```
🔍 ZEBRA PRINT INSTALLATION CHECK
✅ Docker installed (Version: 24.0.5)
✅ Docker daemon running  
✅ Docker permissions OK
✅ Docker Compose available (Version: v2.20.2)
✅ Zebra printer detected (Bus 001 Device 004: ID 0a5f:0129 Zebra ZTC ZD230-203dpi ZPL)
✅ USB device access OK
✅ Port 5000 available
✅ Port 8631 available  
✅ Port 631 in use (system CUPS) - We use port 8631 to avoid conflict
✅ All required files found
✅ Ready for installation! (12/12 checks passed - 100%)

🚀 Next steps:
1. Run: ./zebra.sh start      # Auto-configures printer
2. Run: ./zebra.sh auth       # Setup Cloudflare (one-time)  
3. Run: ./zebra.sh setup      # Configure domain & tunnel
4. Test printing with your domain URL
```

### **Step 2: System Startup (Auto-Configures Everything)**
```bash
./zebra.sh start
```

**What happens automatically:**
- ✅ Downloads optimized Alpine Docker image (288MB)
- ✅ Starts container with proper USB printer access
- ✅ Auto-detects and configures Zebra printer in CUPS
- ✅ Starts API server on port 5000
- ✅ Starts CUPS on port 8631 (avoiding conflicts)
- ✅ System ready in ~15 seconds

### **Step 3: One-Time Cloudflare Setup**
```bash
./zebra.sh auth
```

**What happens automatically:**
- ✅ Installs cloudflared if not present
- ✅ Opens browser for Cloudflare authentication
- ✅ Copies authentication credentials to container
- ✅ Verifies authentication works

### **Step 4: Domain Configuration**
```bash
./zebra.sh setup
```
- Choose option 4: Setup Tunnel
- Choose option 1: Cloudflare Named Tunnel  
- Enter domain: `tln-zebra-01.abcfood.app`
- ✅ Tunnel and DNS records created automatically

---

## 🔧 **Troubleshooting Common User Issues**

### **Docker Not Installed**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Windows: Download Docker Desktop
# macOS: brew install docker
```

### **Docker Permission Denied**
```bash
sudo usermod -aG docker $USER
newgrp docker
# Or restart terminal/logout-login
```

### **Printer Not Detected**
```bash
# Check USB connection
lsusb | grep -i zebra

# Check in container after start
docker exec zebra-print-control lsusb | grep -i zebra
```

### **Port Conflicts**
```bash
# Check what's using ports
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :8631

# Our system automatically avoids common conflicts
```

---

## 📋 **Installation Requirements**

### **Minimum Requirements**
- **OS**: Linux, macOS, Windows with WSL2
- **RAM**: 512MB available
- **Disk**: 1GB free space
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### **Recommended Requirements**  
- **RAM**: 1GB available
- **Disk**: 2GB free space
- **Network**: Internet access for Cloudflare
- **USB**: Direct USB connection to Zebra printer

---

## 🎯 **What Users Need to Do vs Auto-Resolved**

### **User Actions Required (One-Time)**
1. ✋ Install Docker (if not present)
2. ✋ Run `./zebra.sh install` to verify setup
3. ✋ Run `./zebra.sh auth` for Cloudflare authentication
4. ✋ Provide their custom domain name

### **Automatically Resolved**
1. ✅ Port conflict resolution (631 → 8631)
2. ✅ Printer detection and CUPS configuration
3. ✅ Docker image optimization (Alpine 288MB)
4. ✅ Service startup orchestration
5. ✅ USB device access and permissions
6. ✅ Database initialization
7. ✅ Tunnel creation and DNS records
8. ✅ Health checks and monitoring

---

## 🌟 **Deployment Scenarios**

### **Factory/Production Floor**
```bash
# 1. Manager runs on production computer
./zebra.sh install    # Verify computer meets requirements
./zebra.sh start      # Start system, auto-configure printer
./zebra.sh auth       # One-time Cloudflare auth
./zebra.sh setup      # Configure company domain

# 2. Result: Permanent URL for Odoo integration
# https://tln-zebra-01.abcfood.app/print
```

### **IT Department Deployment**
```bash
# 1. Test on staging machine
./zebra.sh install && ./zebra.sh start && ./zebra.sh health

# 2. Deploy to production machines
# Same commands work across all environments
# No machine-specific configuration needed
```

### **Remote Office Setup**
```bash
# 1. Ship computer with printer to remote office
# 2. Remote user runs:
./zebra.sh install    # Verify everything works
./zebra.sh start      # System auto-configures
./zebra.sh setup      # Configure domain for that location

# 3. Each office gets own subdomain:
# tln-zebra-office1.company.com
# tln-zebra-office2.company.com
```

---

## ✅ **Success Criteria**

After installation, users should achieve:
- ✅ **Zero-config printer setup** (automatic CUPS configuration)
- ✅ **No port conflicts** (automatic port mapping)
- ✅ **Permanent URL** (custom domain with SSL)
- ✅ **Immediate testing** (print works right after setup)
- ✅ **Production ready** (robust, monitored, auto-restart)

**Total setup time: 2-5 minutes depending on computer speed** 🎉