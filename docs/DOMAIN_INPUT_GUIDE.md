# 🌐 Custom Domain Input Guide

## ✨ **You Can Now Type Your Domain!**

The system now includes an **interactive domain input** where you can type your custom domain directly in the UI.

---

## 🚀 **How to Use**

### **Step 1: Start the System**
```bash
python3 zebra_control_v2.py
```

### **Step 2: Setup Named Tunnel**
1. Select **Option 4: Setup Tunnel**
2. Choose **Option 1: Cloudflare Named Tunnel**
3. **Type your custom domain** when prompted:

```
🌐 Enter your custom domain: tln-zebra-01.abcfood.app
🎯 Your webhook URL will be: https://tln-zebra-01.abcfood.app/print
✅ Is this correct? (y/n): y
```

### **Step 3: Authentication** (One-time)
```bash
cloudflared tunnel login
```

### **Step 4: Start Tunnel**
1. Select **Option 5: Start Tunnel** 
2. Choose **Option 1: Cloudflare Named**
3. Your permanent URL is ready! 🎉

---

## 📋 **Domain Examples**

You can input domains like:
- `tln-zebra-01.abcfood.app`
- `printer-hq.mycompany.com`
- `zebra-label.mydomain.org`
- `factory-01.manufacturing.net`
- `warehouse-printer.logistics.com`

---

## 🔧 **Features**

### **Smart Validation**
- ✅ Checks domain format
- ✅ Converts to lowercase
- ✅ Removes spaces
- ✅ Validates domain structure

### **Interactive Confirmation**
```
🎯 Your webhook URL will be: https://your-domain.com/print
✅ Is this correct? (y/n): 
```

### **Database Storage**
- ✅ Saves domain configuration
- ✅ Persists between restarts
- ✅ Shows in system status

---

## 🐳 **Docker Usage**

### **Input Domain in Docker**
```bash
# Access container
docker exec -it zebra-print bash

# Run control system
python3 zebra_control_v2.py

# Follow the same steps as above
```

### **Pre-configure Domain**
```bash
# Set domain via command
docker exec -it zebra-print python3 -c "
from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
tunnel = CloudflareNamedTunnel()
tunnel.set_custom_domain('tln-zebra-01.abcfood.app')
"
```

---

## 💡 **Pro Tips**

### **Domain Requirements**
- Must be managed by **Cloudflare DNS**
- Domain should be **active** and **verified**
- Use **subdomains** for organization (e.g., `printer-01.company.com`)

### **Odoo Integration**
1. Get your webhook URL: `https://your-domain.com/print`
2. Add to Odoo webhook configuration
3. Test with sample label data

### **Multiple Locations**
For multiple printers/locations:
- `tln-zebra-01.abcfood.app` (Location 1)
- `tln-zebra-02.abcfood.app` (Location 2)
- `warehouse-printer.abcfood.app` (Warehouse)

---

## 🎯 **Complete Example**

```bash
# 1. Start system
python3 zebra_control_v2.py

# 2. Setup tunnel (Option 4 → Option 1)
🌐 Enter your custom domain: tln-zebra-01.abcfood.app
✅ Is this correct? (y/n): y

# 3. Authenticate (if needed)
cloudflared tunnel login

# 4. Start tunnel (Option 5 → Option 1)
✅ Named tunnel started successfully
🌐 URL: https://tln-zebra-01.abcfood.app
🔗 Webhook URL: https://tln-zebra-01.abcfood.app/print

# 5. Use in Odoo
Webhook URL: https://tln-zebra-01.abcfood.app/print
```

---

**🎉 Your custom domain is now ready for professional Odoo integration!**