#!/bin/bash

# Cloudflare Tunnel Startup Script
# Only starts if ZEBRA_TUNNEL_TYPE=cloudflare and CLOUDFLARE_TOKEN is set

echo "🔍 Checking tunnel configuration..."

if [ "$ZEBRA_TUNNEL_TYPE" = "cloudflare" ] && [ -n "$CLOUDFLARE_TOKEN" ]; then
    echo "✅ Cloudflare tunnel configured, starting..."
    echo "🌐 Domain: $ZEBRA_DOMAIN"
    echo "🔑 Token: ${CLOUDFLARE_TOKEN:0:20}..."
    
    # Start cloudflared tunnel with token
    exec cloudflared tunnel run --token "$CLOUDFLARE_TOKEN"
else
    echo "⚠️ Cloudflare tunnel not configured (ZEBRA_TUNNEL_TYPE=$ZEBRA_TUNNEL_TYPE, CLOUDFLARE_TOKEN set: $([ -n "$CLOUDFLARE_TOKEN" ] && echo "yes" || echo "no"))"
    echo "ℹ️ Tunnel service will sleep (no tunnel needed)"
    
    # Keep the process alive but do nothing
    while true; do
        sleep 3600
    done
fi