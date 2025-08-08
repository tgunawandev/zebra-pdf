# 🚀 Quick Cloudflare Setup (2 minutes)

## ⚡ **Simple Setup Process**

### **Step 1: Start System**
```bash
./zebra.sh start
```

### **Step 2: Setup Cloudflare (One-time)**
```bash
./zebra.sh auth
```
This will:
- Install cloudflared if needed
- Open browser for Cloudflare authentication  
- Copy auth credentials to container
- ✅ Ready for tunnel setup

### **Step 3: Configure Domain & Tunnel**
```bash
./zebra.sh setup
```
Choose:
- Option 4: Setup Tunnel
- Option 1: Cloudflare Named Tunnel
- Enter your domain (e.g., `tln-zebra-01.abcfood.app`)

### **Step 4: Test**
```bash
curl -X POST https://tln-zebra-01.abcfood.app/print \
  -H "Content-Type: application/json" \
  -d '{"labels":[{"title":"TEST","date":"08/08/25","qr_code":"123"}]}'
```

---

## 🎯 **Complete Setup Example**

```bash
# 1. Clone and start (auto-configures printer)
git clone <repo>
cd zebra-pdf  
./zebra.sh start        # ✅ Printer auto-configured

# 2. One-time Cloudflare auth
./zebra.sh auth         # ✅ Browser opens, authenticate

# 3. Setup domain and tunnel
./zebra.sh setup        # ✅ Choose Cloudflare, enter domain
                        # ✅ Tunnel and DNS created

# 4. Ready!
curl https://your-domain.com/print -X POST ...
```

**Total time: ~2 minutes for complete setup!** 🎉