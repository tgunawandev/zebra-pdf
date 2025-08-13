FROM alpine:3.18

# Install system dependencies
RUN apk add --no-cache \
    python3 py3-pip \
    cups cups-client cups-filters \
    curl bash usbutils \
    supervisor \
    && rm -rf /var/cache/apk/*

# Install Cloudflare tunnel (cloudflared)
RUN wget -O cloudflared \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x cloudflared \
    && mv cloudflared /usr/local/bin/ \
    || echo "Warning: Could not install cloudflared - tunnel features will be limited"

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and log file
RUN mkdir -p /var/log/zebra-print /app/data /var/log/supervisor && \
    touch /app/print_api.log && \
    chmod 666 /app/print_api.log

# Configure CUPS for printer access
RUN adduser root lpadmin && \
    sed -i 's/^Listen localhost:631/Listen 0.0.0.0:631/' /etc/cups/cupsd.conf && \
    sed -i 's/<Location \/>/<Location \/>\n  Allow all/' /etc/cups/cupsd.conf

# Copy Alpine-specific supervisor configuration
COPY docker/supervisor-alpine.conf /etc/supervisor/conf.d/zebra-print.conf

# Create printer detection and setup scripts
COPY docker/detect-printer.sh /usr/local/bin/detect-printer.sh
COPY docker/auto-printer-setup.sh /app/docker/auto-printer-setup.sh
RUN chmod +x /usr/local/bin/detect-printer.sh /app/docker/auto-printer-setup.sh

# Create Alpine-specific entrypoint script
COPY docker/entrypoint-alpine.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 5000 631

# Set environment variables
ENV ZEBRA_BASE_DIR=/app
ENV ZEBRA_API_HOST=0.0.0.0
ENV ZEBRA_API_PORT=5000
ENV ZEBRA_DB_PATH=/app/data/zebra_print.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Use Alpine entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/zebra-print.conf", "-n"]