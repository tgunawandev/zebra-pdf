# Docker Compose Usage for Zebra PDF Label Printing System

## Quick Start

### 1. Build and Start the Service
```bash
docker compose up -d
```

### 2. Check Service Status
```bash
docker compose ps
```

### 3. Check Application Health
```bash
curl http://localhost:5000/health
```

## Available Commands

### Service Management
```bash
# Start services in background
docker compose up -d

# Start services with logs visible
docker compose up

# Stop services
docker compose down

# Restart services
docker compose restart

# Stop and remove containers and networks
docker compose down --volumes
```

### Monitoring
```bash
# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View last 50 log lines
docker compose logs --tail=50

# Check service status
docker compose ps
```

### Container Access
```bash
# Open shell in running container
docker compose exec zebra-print /bin/bash

# Run a command in container
docker compose exec zebra-print ls -la /app
```

### Maintenance
```bash
# Rebuild images
docker compose build

# Rebuild and restart
docker compose up -d --build

# View container resource usage
docker stats zebra-print-control
```

## Available Endpoints

- **API Server**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **CUPS Interface**: http://localhost:8631

## Testing the API

### Generate API Token
```bash
curl -X POST http://localhost:5000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "description": "Test token"}'
```

### Send Test Print Job
```bash
# First get a token
TOKEN=$(curl -s -X POST http://localhost:5000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}' | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Send print request
curl -X POST http://localhost:5000/print \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "labels": [
      {
        "title": "Test Label",
        "date": "2024-01-01", 
        "qr_code": "TEST123"
      }
    ]
  }'
```

### List Available Printers
```bash
curl http://localhost:5000/printers
```

## File Structure

- **docker-compose.yml**: Main Docker Compose configuration
- **Dockerfile.minimal**: Optimized container image
- **standalone_api.py**: Main API application
- **requirements.txt**: Python dependencies

## Environment Variables

Set in `docker-compose.yml`:
- `ZEBRA_API_HOST`: API host (default: 0.0.0.0)
- `ZEBRA_API_PORT`: API port (default: 5000)
- `ZEBRA_PRINTER_NAME`: Target printer name
- `ZEBRA_DB_PATH`: Database file path

## Data Persistence

- Application data: `/app/data` (mapped to Docker volume)
- Logs: `/var/log/zebra-print` (mapped to Docker volume)

## Troubleshooting

### Check if service is running
```bash
docker compose ps
```

### View recent logs
```bash
docker compose logs --tail=20
```

### Test connectivity
```bash
curl http://localhost:5000/health
```

### Restart if needed
```bash
docker compose restart
```