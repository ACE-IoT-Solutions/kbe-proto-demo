# Makefile for KBE PoC Demo Portal
# Provides convenient shortcuts for Docker and development operations

.PHONY: help build run stop logs clean test shell health

# Default target
.DEFAULT_GOAL := help

# Variables
IMAGE_NAME := kbe-demo-portal
CONTAINER_NAME := kbe-demo
PORT := 8008

help: ## Show this help message
	@echo "KBE PoC Demo Portal - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Docker operations
build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME) .

build-no-cache: ## Build Docker image without cache
	@echo "Building Docker image (no cache)..."
	docker build --no-cache -t $(IMAGE_NAME) .

run: ## Run container in detached mode
	@echo "Starting container..."
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):$(PORT) $(IMAGE_NAME)
	@echo "Container started at http://localhost:$(PORT)"

run-fg: ## Run container in foreground
	@echo "Starting container in foreground..."
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT):$(PORT) $(IMAGE_NAME)

stop: ## Stop and remove container
	@echo "Stopping container..."
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true

restart: stop run ## Restart container

logs: ## View container logs
	docker logs -f $(CONTAINER_NAME)

shell: ## Access container shell
	docker exec -it $(CONTAINER_NAME) /bin/bash

health: ## Check container health
	@docker inspect --format='{{.State.Health.Status}}' $(CONTAINER_NAME) 2>/dev/null || echo "Container not running"

# Docker Compose operations
up: ## Start services with docker-compose
	docker compose up -d

down: ## Stop services with docker-compose
	docker compose down

compose-logs: ## View docker-compose logs
	docker compose logs -f

compose-build: ## Build services with docker-compose
	docker compose build

# Development
dev: ## Run in development mode with hot reload
	docker compose -f docker-compose.yml up

dev-build: ## Build and run in development mode
	docker compose -f docker-compose.yml up --build

# Testing
test: ## Run tests in container
	docker run --rm $(IMAGE_NAME) python -m pytest tests/ -v

test-local: ## Run tests locally (requires uv)
	uv run pytest tests/ -v

coverage: ## Run tests with coverage
	docker run --rm $(IMAGE_NAME) python -m pytest tests/ --cov=src --cov-report=html

# Maintenance
clean: ## Remove container and image
	@echo "Cleaning up..."
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true
	docker rmi $(IMAGE_NAME) 2>/dev/null || true

clean-all: ## Remove all containers, images, and volumes
	@echo "Deep cleaning..."
	docker compose down -v
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true
	docker rmi $(IMAGE_NAME) 2>/dev/null || true
	docker system prune -f

prune: ## Remove unused Docker resources
	docker system prune -f

# Inspection
ps: ## List running containers
	docker ps --filter "name=$(CONTAINER_NAME)"

stats: ## Show container resource usage
	docker stats $(CONTAINER_NAME)

inspect: ## Inspect container details
	docker inspect $(CONTAINER_NAME)

size: ## Show image size
	docker images $(IMAGE_NAME)

# Quick commands
quick-start: build run ## Build and run in one command
	@echo "KBE Demo Portal is running at http://localhost:$(PORT)"
	@echo "Knowledge Graph: http://localhost:$(PORT)/static/graph.html"
	@echo "API Docs: http://localhost:$(PORT)/docs"

quick-dev: compose-build up ## Build and start development environment
	@echo "Development environment started"

# Production deployment
deploy: ## Deploy to production (requires configuration)
	@echo "Deploying to production..."
	@echo "This is a placeholder - configure for your deployment environment"

# Utility commands
version: ## Show versions
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker compose version)"
	@echo "Python in image: $$(docker run --rm $(IMAGE_NAME) python --version || echo 'Image not built')"

lint: ## Run linting (requires local uv)
	uv run ruff check src/

format: ## Format code (requires local uv)
	uv run ruff format src/

# Database operations (if needed in future)
# migrate: ## Run database migrations
# 	docker exec $(CONTAINER_NAME) python -m alembic upgrade head

# Backup operations (if needed in future)
# backup: ## Backup application data
# 	@echo "Creating backup..."
# 	docker exec $(CONTAINER_NAME) tar -czf /tmp/backup.tar.gz /app/data

.PHONY: build build-no-cache run run-fg stop restart logs shell health \
        up down compose-logs compose-build dev dev-build \
        test test-local coverage clean clean-all prune \
        ps stats inspect size quick-start quick-dev deploy version lint format
