# 🔌 Port Conflict Resolution Guide

## ❌ **The Problem: Port Already In Use**

**Common error:**
```
Address in use
Port 5000 is in use by another program
```

**Root cause:** Multiple services competing for the same ports (5000, 8631, 631)

---

## ✅ **Solution 1: Smart Port Management (Recommended)**

### **Use Smart Mode with Auto-Detection**
```bash
# Instead of ./zebra.sh start, use:
./zebra-smart.sh start
```

**What it does automatically:**
- 🔍 Scans for port conflicts
- ✅ Finds available alternative ports  
- 🔧 Updates configuration automatically
- 📊 Shows final port mapping

**Example output:**
```
🔍 Detecting available ports...
⚠️ Port 5000 (API) is in use
✅ Using port 5001 for API
✅ Port 8631 (CUPS) available

📊 Port Configuration:
  • Host API Port:  5001 → Container 5000
  • Host CUPS Port: 8631 → Container 631

✅ System started successfully!
🌐 Services available at:
  • API Server:    http://localhost:5001
  • CUPS Admin:    http://localhost:8631
```

---

## ✅ **Solution 2: Manual Port Resolution**

### **Step 1: Find Conflicting Processes**
```bash
# Check what's using port 5000
sudo netstat -tlnp | grep :5000
# or
sudo ss -tlnp | grep :5000

# Example output:
# tcp  0  0  127.0.0.1:5000  *  LISTEN  1234/python
```

### **Step 2: Stop Conflicting Service (if safe)**
```bash
# Kill the process using port 5000
sudo kill 1234

# Or stop the service
sudo systemctl stop <service-name>
```

### **Step 3: Use Port Resolution Script**
```bash
# Automatically find and configure alternative ports
./find-free-port.sh

# Restart with new configuration
./zebra.sh start
```

---

## ✅ **Solution 3: Manual Port Configuration**

### **Change Ports in docker-compose.yml**
```yaml
# Edit docker-compose.yml
ports:
  - "5001:5000"  # API: Changed from 5000 to 5001
  - "8632:631"   # CUPS: Changed from 8631 to 8632
```

### **Update Environment Variables**
```bash
# Set custom ports
export ZEBRA_API_PORT=5001
export ZEBRA_CUPS_PORT=8632

# Start system
./zebra.sh start
```

### **Update All References**
```bash
# Update scripts to use new ports
sed -i 's/localhost:5000/localhost:5001/g' zebra.sh
sed -i 's/localhost:8631/localhost:8632/g' zebra.sh

# Update documentation
sed -i 's/5000/5001/g' docs/*.md
```

---

## 🎯 **Production Deployment Strategy**

### **For Multiple Installations**
```bash
# Each installation gets unique ports
# Location 1: API=5000, CUPS=8631
# Location 2: API=5001, CUPS=8632  
# Location 3: API=5002, CUPS=8633

# Script automatically handles this:
./zebra-smart.sh start
```

### **For Load Balancer Setup**
```bash
# Use different ports for each instance
docker-compose -f docker-compose-smart.yml up -d --scale zebra-print=3

# Ports automatically assigned:
# Instance 1: 5000, 8631
# Instance 2: 5001, 8632
# Instance 3: 5002, 8633
```

---

## 🔍 **Debugging Port Issues**

### **Check Current Port Usage**
```bash
# Show all Zebra-related ports
./zebra-smart.sh ports

# Check specific port
sudo netstat -tlnp | grep :5000
sudo lsof -i :5000
```

### **Container Port Mapping**
```bash
# See what ports Docker is using
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Check port mapping inside container
docker exec zebra-print-control netstat -tln
```

### **Test Port Accessibility**
```bash
# Test API port from host
curl http://localhost:5001/health

# Test from another machine
curl http://your-ip:5001/health
```

---

## 🛠️ **Advanced Solutions**

### **1. Environment-Based Configuration**
```bash
# Create .env file for custom ports
cat > .env << EOF
ZEBRA_API_PORT=5010
ZEBRA_CUPS_PORT=8640
EOF

# Start with custom configuration
./zebra-smart.sh start
```

### **2. Docker Network Isolation**
```bash
# Use Docker internal networking (no host conflicts)
docker network create zebra-network

# Update docker-compose.yml to use internal networking
# External access via reverse proxy only
```

### **3. Reverse Proxy Setup**
```bash
# Use nginx/traefik to handle multiple services
# Map different paths to different ports:
# /zebra1/ → localhost:5000
# /zebra2/ → localhost:5001
```

---

## 📋 **Port Conflict Prevention Checklist**

### **Before Deployment**
- [ ] Run `./zebra-smart.sh ports` to check current usage
- [ ] Use `./zebra-smart.sh start` for automatic resolution
- [ ] Test all endpoints after startup
- [ ] Document final port configuration

### **For Multiple Deployments**
- [ ] Use smart mode for automatic port allocation
- [ ] Document port assignments per location
- [ ] Set up monitoring for port conflicts
- [ ] Create backup port configuration

---

## 🎉 **Recommended Workflow**

### **For New Installations**
```bash
# 1. Always use smart mode
./zebra-smart.sh start

# 2. Verify ports
./zebra-smart.sh ports

# 3. Test functionality
curl http://localhost:$(cat .port-config | grep API_PORT | cut -d= -f2)/health

# 4. Proceed with tunnel setup
./zebra.sh setup
```

### **For Troubleshooting**
```bash
# 1. Check what's wrong
./zebra-smart.sh ports

# 2. Resolve conflicts
./zebra-smart.sh resolve

# 3. Restart with new config
./zebra-smart.sh restart

# 4. Verify working
./zebra.sh health
```

**Result: Port conflicts never block deployment!** 🎉