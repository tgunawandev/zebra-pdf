# 🌐 Cloudflare Tunnel - PERMANENT URL Solution

**Problem solved!** No more copying URLs every time - get a **permanent URL** that never changes.

## ✅ **Why Cloudflare Tunnel > Ngrok:**

| Feature | Ngrok | Cloudflare |
|---------|--------|-------------|
| URL Changes | ❌ Every restart | ✅ **NEVER** |
| Setup in Odoo | ❌ Copy URL each time | ✅ **Set once, forget** |
| Free Usage | Limited | Better limits |
| Performance | Good | Faster (CDN) |
| Reliability | Good | Better (enterprise) |

## 🚀 **One-Time Setup:**

```bash
python cloudflare_setup.py
```

**What happens:**
1. 🔐 Login to Cloudflare (browser opens once)
2. 🔧 Creates permanent tunnel 
3. 🌐 Gets your permanent URL: `https://zebra-printer-abc123.trycloudflare.com`
4. ✅ **URL NEVER CHANGES!**

## 📋 **Daily Usage:**

```bash
# Start tunnel (permanent URL)
python cloudflare_start.py

# Check status  
python cloudflare_status.py

# Test tunnel
python cloudflare_test.py

# Stop tunnel
python cloudflare_stop.py
```

## 🎯 **Odoo Integration:**

1. **Run setup once:**
   ```bash
   python cloudflare_setup.py
   ```

2. **Get your permanent URL:**
   ```
   🌐 PERMANENT URL: https://zebra-printer-abc123.trycloudflare.com
   ```

3. **Configure in Odoo ONCE:**
   - Webhook URL: `https://zebra-printer-abc123.trycloudflare.com/print`
   - Method: POST
   - Content-Type: application/json

4. **Start tunnel when needed:**
   ```bash
   python cloudflare_start.py
   ```

5. **✅ DONE! URL never changes again!**

## 🔄 **Typical Workflow:**

```bash
# Once per day/session
python start_server.py         # Start local API
python cloudflare_start.py     # Start tunnel

# Your permanent URL is now live
# Odoo can send requests immediately
# No configuration changes needed!
```

## 🧪 **Testing:**

```bash
# Test your permanent URL
python cloudflare_test.py

# Manual test with curl
curl https://your-permanent-url.trycloudflare.com/health

# Test print
curl -X POST https://your-permanent-url.trycloudflare.com/print \
  -H "Content-Type: application/json" \
  -d '{"labels": [{"title": "TEST", "date": "08/08/25", "qr_code": "123"}]}'
```

## 💡 **Key Benefits:**

- ✅ **Set URL once in Odoo**
- ✅ **Never copy/paste URLs again**  
- ✅ **Faster than ngrok**
- ✅ **More reliable**
- ✅ **Better security**
- ✅ **Free usage**

## 🛠️ **Commands Summary:**

| Command | Purpose |
|---------|---------|
| `python cloudflare_setup.py` | One-time setup (creates permanent URL) |
| `python cloudflare_start.py` | Start tunnel |
| `python cloudflare_stop.py` | Stop tunnel |
| `python cloudflare_status.py` | Check tunnel status |
| `python cloudflare_test.py` | Test tunnel + print |

---

**🎉 Perfect solution! Set up once, use forever with the same URL!**