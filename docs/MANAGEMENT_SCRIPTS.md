# 🛠️ Management Scripts Guide

## ✨ **Cross-Platform Management**

The Zebra Print Control System includes sophisticated management scripts for both Windows and Linux, providing the **best UX** for managing your containerized printing system.

---

## 🐧 **Linux Management**

### **Primary Script: `zebra.sh`**
```bash
# Make executable
chmod +x zebra.sh

# Basic usage
./zebra.sh start        # Start the system
./zebra.sh status       # Check system status  
./zebra.sh setup        # Interactive setup
./zebra.sh domain       # Configure custom domain
./zebra.sh health       # Comprehensive health check
./zebra.sh help         # Show all commands
```

### **Key Features**
- ✅ **Modern Docker Commands**: Uses `docker compose` (not deprecated `docker-compose`)
- ✅ **Color-coded Output**: Beautiful terminal colors and emojis
- ✅ **USB Detection**: Automatically detects Zebra printers
- ✅ **Health Monitoring**: Comprehensive system health checks
- ✅ **Smart Validation**: Domain format validation and confirmation
- ✅ **Error Handling**: Graceful error handling with helpful messages

---

## 🪟 **Windows Management**

### **Three Options Available**

#### **1. Batch Script: `zebra.bat`**
```cmd
REM Basic Windows command prompt support
zebra.bat start         REM Start the system
zebra.bat status        REM Check status
zebra.bat setup         REM Interactive setup
zebra.bat help          REM Show commands
```

#### **2. PowerShell Script: `zebra.ps1` (Recommended)**  
```powershell
# Advanced Windows management with PowerShell features
.\zebra.ps1 start
.\zebra.ps1 status
.\zebra.ps1 domain -Domain "tln-zebra-01.abcfood.app"
.\zebra.ps1 firewall    # Configure Windows Firewall
.\zebra.ps1 desktop     # Create desktop shortcuts
.\zebra.ps1 health      # Advanced health monitoring
```

#### **3. PowerShell with Parameters**
```powershell
# Domain configuration with parameter
.\zebra.ps1 domain -Domain "your-domain.com"

# Force cleanup without confirmation
.\zebra.ps1 clean -Force

# Get help
.\zebra.ps1 help
```

### **Windows-Specific Features**
- ✅ **USB Device Detection**: Uses WMI to detect Zebra printers
- ✅ **Firewall Configuration**: Automatically configure Windows Firewall
- ✅ **Desktop Shortcuts**: Create shortcuts for common operations
- ✅ **Service Installation**: Install as Windows service (planned)
- ✅ **Admin Privileges**: Detect and handle admin requirements

---

## 🎯 **Best UX Practices Implemented**

### **Universal Features**
- **Smart Requirements Check**: Validates Docker and Docker Compose
- **Progressive Disclosure**: Shows only relevant information at each step
- **Confirmation Steps**: Asks for confirmation on destructive operations
- **Status Feedback**: Real-time feedback with progress indicators
- **Error Recovery**: Helpful error messages with suggested solutions

### **Platform-Specific Optimizations**

#### **Linux UX**
- **Shell Completion**: Tab completion support
- **Signal Handling**: Graceful handling of Ctrl+C
- **Color Support**: Terminal color detection and fallbacks
- **Process Management**: Proper PID file handling

#### **Windows UX**
- **PowerShell Integration**: Rich object handling and pipeline support
- **Registry Integration**: Windows-specific configuration storage
- **Event Log**: Windows Event Log integration
- **UAC Handling**: Proper User Account Control handling

---

## 📋 **Complete Command Reference**

### **Container Management**
```bash
./zebra.sh start      # Build and start system
./zebra.sh stop       # Stop system gracefully  
./zebra.sh restart    # Restart system
./zebra.sh status     # Show detailed status
./zebra.sh logs       # Show container logs (follow mode)
./zebra.sh shell      # Access interactive container shell
```

### **Configuration**
```bash
./zebra.sh setup      # Interactive setup wizard
./zebra.sh domain     # Configure custom domain interactively
./zebra.sh tunnel     # Tunnel configuration (same as setup)
```

### **Testing & Monitoring**
```bash
./zebra.sh health     # Comprehensive health check
./zebra.sh printer    # Detailed printer diagnostics
./zebra.sh api        # Test all API endpoints
./zebra.sh test       # Run full test suite
```

### **Maintenance**
```bash
./zebra.sh backup     # Backup configuration to timestamped file
./zebra.sh restore    # Restore from backup file
./zebra.sh clean      # Remove containers and images
./zebra.sh version    # Show version information
```

---

## 🎨 **UX Design Philosophy**

### **1. Progressive Complexity**
- **Simple Start**: `./zebra.sh start` gets you running immediately
- **Guided Setup**: `./zebra.sh setup` walks through configuration
- **Advanced Options**: Full control available when needed

### **2. Visual Feedback**
```
🚀 Starting Zebra Print Control System...
✅ Zebra printer detected  
🌐 Services available at:
  • API Server:    http://localhost:5000
  • Health Check:  http://localhost:5000/health
💡 Next steps:
  • Run: ./zebra.sh setup    (for initial configuration)
```

### **3. Error Prevention**
- **Domain Validation**: Prevents invalid domain formats
- **Confirmation Prompts**: Asks before destructive operations
- **Requirements Check**: Validates prerequisites before starting
- **Status Awareness**: Won't start if already running

### **4. Help Discovery**
- **Context-Sensitive Help**: Relevant suggestions in error messages
- **Command Examples**: Every help section includes examples  
- **Progressive Disclosure**: Basic commands shown first, advanced later

---

## 🚀 **Quick Start Examples**

### **Complete Setup Flow**
```bash
# 1. Start the system
./zebra.sh start

# 2. Configure your domain
./zebra.sh setup
# Enter domain: tln-zebra-01.abcfood.app

# 3. Check everything is working
./zebra.sh health

# 4. Get your webhook URL
./zebra.sh status
# Shows: Webhook URL: https://tln-zebra-01.abcfood.app/print
```

### **Daily Operations**
```bash
# Check status
./zebra.sh status

# View logs
./zebra.sh logs

# Test printer
./zebra.sh printer

# Health check
./zebra.sh health
```

### **Maintenance**
```bash
# Backup before changes
./zebra.sh backup

# Update and restart
./zebra.sh restart

# Clean up if needed
./zebra.sh clean
```

---

## 🏆 **Why This UX is Superior**

1. **Cross-Platform Consistency**: Same commands work on Linux and Windows
2. **Modern Docker Support**: Uses current `docker compose` commands
3. **Beautiful Output**: Colors, emojis, and clear formatting
4. **Smart Defaults**: Sensible defaults that work out of the box
5. **Error Prevention**: Validates input and prevents common mistakes
6. **Recovery Oriented**: Every error includes suggested solutions
7. **Progressive Complexity**: Simple for beginners, powerful for experts

**This management system provides the best possible UX for both Windows and Linux users managing containerized Zebra printing systems!** 🎉