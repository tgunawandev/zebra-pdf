# 🌐 Cloudflare Domain Setup Guide

## ❌ **Common Issue: Domain Not Managed by Cloudflare**

**Error you're seeing:**
```
❌ Setup failed: Failed to create DNS record: zebra-print is neither 
the ID nor the name of any of your tunnels
```

**Root cause:** The domain `abcfood.app` needs to be added to Cloudflare DNS first.

---

## 🔧 **Solution: Add Domain to Cloudflare**

### **Step 1: Add Domain to Cloudflare**
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click **"Add a Site"**
3. Enter your domain: `abcfood.app`
4. Choose plan (Free is fine)
5. Click **"Add Site"**

### **Step 2: Update Nameservers**
Cloudflare will show you nameservers like:
```
ns1.cloudflare.com
ns2.cloudflare.com
```

**Update at your domain registrar:**
- Go to your domain registrar (GoDaddy, Namecheap, etc.)
- Update nameservers to Cloudflare's nameservers
- **Wait 24-48 hours** for propagation

### **Step 3: Verify Domain is Active**
1. In Cloudflare dashboard, check domain status
2. Should show **"Active"** (green checkmark)
3. DNS tab should be available

---

## ✅ **Alternative: Use Your Own Domain**

If you don't want to change nameservers, use a domain you already manage in Cloudflare:

### **Option 1: Existing Cloudflare Domain**
```bash
# Use a domain already in your Cloudflare account
./zebra.sh setup
# Enter: tln-zebra-01.yourexistingdomain.com
```

### **Option 2: Cloudflare Subdomain**
```bash
# Get a free Cloudflare subdomain
# Visit: https://www.cloudflare.com/products/registrar/
# Or use existing subdomain you control
```

### **Option 3: Quick Tunnel (Temporary)**
```bash
./zebra.sh setup
# Choose option 2: Cloudflare Quick Tunnel (Temporary URL)
# Get instant random URL like: https://abc123.trycloudflare.com
```

---

## 🎯 **Recommended Solution**

### **For Production: Use Company Domain**
1. **Add company domain to Cloudflare**: `yourcompany.com`
2. **Use subdomains for locations**: 
   - `zebra-warehouse.yourcompany.com`
   - `zebra-office1.yourcompany.com`
   - `zebra-office2.yourcompany.com`

### **For Testing: Use Quick Tunnel**
```bash
./zebra.sh setup
# Choose: Cloudflare Quick Tunnel
# Get instant URL for testing
```

---

## 🚀 **Complete Working Example**

### **Scenario: Company has `mycompany.com` in Cloudflare**
```bash
# 1. Start system
./zebra.sh start

# 2. Setup authentication  
./zebra.sh auth

# 3. Configure with company subdomain
./zebra.sh setup
# Enter: zebra-printer.mycompany.com
# ✅ Works immediately!

# 4. Test
curl -X POST https://zebra-printer.mycompany.com/print \
  -H "Content-Type: application/json" \
  -d '{"labels":[{"title":"TEST","date":"08/08/25","qr_code":"123"}]}'
```

---

## 💡 **Quick Fix for Your Current Situation**

Since `abcfood.app` is not in Cloudflare DNS:

```bash
# Use temporary tunnel for immediate testing
./zebra.sh setup
# Choose option 2: Cloudflare Quick Tunnel (Temporary URL)
# Get random URL like: https://abc123-def456-ghi789.trycloudflare.com

# Test printing immediately:
curl -X POST https://abc123-def456-ghi789.trycloudflare.com/print \
  -H "Content-Type: application/json" \
  -d '{"labels":[{"title":"QUICK-TEST","date":"08/08/25","qr_code":"NOW"}]}'
```

**This gives you a working URL immediately while you set up the permanent domain!** 🎉