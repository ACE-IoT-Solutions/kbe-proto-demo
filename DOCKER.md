# Docker Deployment Guide - KBE PoC Demo Portal

## Overview

This guide covers building and running the KBE Demo Portal using Docker with Astral UV for fast dependency management.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose 2.0+ (optional, for compose deployment)

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker compose up -d

# View logs
docker compose logs -f kbe-demo

# Stop the container
docker compose down
```

### Using Docker CLI

```bash
# Build the image
docker build -t kbe-demo-portal .

# Run the container
docker run -d \
  --name kbe-demo \
  -p 8008:8008 \
  kbe-demo-portal

# View logs
docker logs -f kbe-demo

# Stop the container
docker stop kbe-demo
docker rm kbe-demo
```

## Access the Application

Once running, access the application at:

- **Demo Portal**: http://localhost:8008/
- **Knowledge Graph**: http://localhost:8008/static/graph.html
- **API Docs**: http://localhost:8008/docs
- **Health Check**: http://localhost:8008/health

## Multi-Stage Build Details

The Dockerfile uses a multi-stage build for optimal image size:

### Stage 1: Builder (ghcr.io/astral-sh/uv:python3.13-bookworm-slim)
- Installs dependencies using UV (150x faster than pip)
- Compiles bytecode for faster startup
- Uses layer caching for dependencies

### Stage 2: Runtime (python:3.13-slim-bookworm)
- Minimal Python runtime
- Only production dependencies
- Non-root user for security
- Built-in health check

## Build Arguments & Environment Variables

### Build-time Arguments

```bash
docker build \
  --build-arg PYTHON_VERSION=3.13 \
  -t kbe-demo-portal .
```

### Runtime Environment Variables

```yaml
environment:
  - ENV=production              # Environment (development/production)
  - LOG_LEVEL=info             # Logging level (debug/info/warning/error)
  - PORT=8008                  # Application port (default: 8008)
```

Example with custom environment:

```bash
docker run -d \
  --name kbe-demo \
  -p 8008:8008 \
  -e LOG_LEVEL=debug \
  -e ENV=development \
  kbe-demo-portal
```

## Production Deployment

### With HTTPS Reverse Proxy (Recommended)

Use with Nginx or Traefik for production:

```yaml
# docker-compose.yml with Nginx
version: '3.8'

services:
  kbe-demo:
    build: .
    container_name: kbe-demo-portal
    expose:
      - "8008"
    environment:
      - ENV=production
    networks:
      - web

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - kbe-demo
    networks:
      - web

networks:
  web:
    driver: bridge
```

### Health Checks

The container includes a built-in health check:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' kbe-demo

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' kbe-demo
```

## Development Workflow

### Local Development with Volume Mounts

For active development, mount source code:

```yaml
# docker-compose.dev.yml
services:
  kbe-demo:
    build: .
    volumes:
      - ./src:/app/src
    environment:
      - ENV=development
      - LOG_LEVEL=debug
    command: python -m uvicorn src.main:app --host 0.0.0.0 --port 8008 --reload
```

Run with:
```bash
docker compose -f docker-compose.dev.yml up
```

### Debugging

Access container shell:

```bash
# Using docker exec
docker exec -it kbe-demo /bin/bash

# Using docker compose
docker compose exec kbe-demo /bin/bash
```

View real-time logs:

```bash
# All logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100

# Filter by service
docker compose logs -f kbe-demo
```

## Image Optimization

### Current Image Size

The multi-stage build produces a compact image:

```bash
# Check image size
docker images kbe-demo-portal

# Typical sizes:
# - Builder stage: ~500MB
# - Final image: ~150-200MB
```

### Further Optimization

For even smaller images, use Alpine:

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder
# ... (same build steps)

FROM python:3.13-alpine
# ... (adjust runtime dependencies)
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker logs kbe-demo
```

Common issues:
- Port 8008 already in use: Change `-p 8009:8008`
- Permission errors: Check file ownership
- Missing dependencies: Rebuild with `--no-cache`

### Dependencies not installing

Clear build cache:
```bash
docker build --no-cache -t kbe-demo-portal .
```

### Performance issues

Check resource limits:
```bash
docker stats kbe-demo
```

Adjust resources in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
```

## Security Considerations

### Non-root User

The container runs as non-root user `appuser` for security.

### Secrets Management

Never commit secrets to the image. Use environment variables or Docker secrets:

```bash
# Using environment file
docker run --env-file .env.production kbe-demo-portal

# Using Docker secrets (Swarm)
docker secret create api_key ./api_key.txt
docker service create --secret api_key kbe-demo-portal
```

### Network Isolation

Use custom networks for isolation:

```yaml
networks:
  frontend:
  backend:
    internal: true  # No external access
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t kbe-demo-portal .

      - name: Run tests in container
        run: |
          docker run --rm kbe-demo-portal \
            python -m pytest tests/ -v

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag kbe-demo-portal your-registry/kbe-demo-portal:latest
          docker push your-registry/kbe-demo-portal:latest
```

## Monitoring

### Prometheus Metrics (Future Enhancement)

Add prometheus metrics endpoint:

```python
# In src/main.py
from prometheus_fastapi_instrumentator import Instrumentator

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)
```

Access metrics at: http://localhost:8008/metrics

## Scaling

### Horizontal Scaling

Use Docker Swarm or Kubernetes:

```bash
# Docker Swarm
docker service create \
  --name kbe-demo \
  --replicas 3 \
  --publish 8008:8008 \
  kbe-demo-portal
```

### Load Balancing

Use Nginx or HAProxy to distribute traffic:

```nginx
upstream kbe-backend {
    server kbe-demo-1:8008;
    server kbe-demo-2:8008;
    server kbe-demo-3:8008;
}
```

## Backup & Restore

### Export Container State

```bash
# Export logs
docker logs kbe-demo > kbe-demo-logs-$(date +%Y%m%d).log

# Commit container state (if needed)
docker commit kbe-demo kbe-demo-backup:$(date +%Y%m%d)
```

## References

- **Astral UV**: https://github.com/astral-sh/uv
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/docker/
- **Multi-stage Builds**: https://docs.docker.com/build/building/multi-stage/

---

*Docker configuration for KBE PoC Demo Portal*
*Built with Astral UV for blazing-fast dependency management* ⚡
