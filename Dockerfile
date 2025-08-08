FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    cups \
    cups-client \
    cups-bsd \
    curl \
    wget \
    usbutils \
    lsb-release \
    gnupg2 \
    software-properties-common \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Cloudflare tunnel
RUN curl -L --output cloudflared.deb \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
    && dpkg -i cloudflared.deb \
    && rm cloudflared.deb

# Install ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list \
    && apt update && apt install ngrok \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/zebra-print \
    && mkdir -p /app/data \
    && chmod +x zebra_control_v2.py

# Configure CUPS for printer access
RUN usermod -a -G lpadmin root \
    && systemctl enable cups

# Create supervisor configuration for services
RUN mkdir -p /etc/supervisor/conf.d
COPY docker/supervisor.conf /etc/supervisor/conf.d/zebra-print.conf

# Create printer detection script
COPY docker/detect-printer.sh /usr/local/bin/detect-printer.sh
RUN chmod +x /usr/local/bin/detect-printer.sh

# Create entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
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

# Use custom entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]