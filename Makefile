# Makefile (Root directory)
.PHONY: build up down logs clean test help dev prod

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services in production mode"
	@echo "  dev       - Start all services in development mode"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Remove all containers, images, and volumes"
	@echo "  test      - Run tests for all services"
	@echo "  health    - Check health of all services"

# Build all images
build:
	docker-compose build

# Start production environment
up: build
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "User Service: http://localhost:5001"
	@echo "Task Service: http://localhost:5002"

# Start development environment
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
	@echo "Development environment started"

# Stop all services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Clean everything
clean:
	docker-compose down -v --remove-orphans
	docker system prune -af
	docker volume prune -f

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:5001/health || echo "User Service: UNHEALTHY"
	@curl -f http://localhost:5002/health || echo "Task Service: UNHEALTHY"
	@curl -f http://localhost:3000 || echo "Frontend: UNHEALTHY"

# Run tests
test:
	@echo "Running User Service tests..."
	@cd user_service && python test_service.py
	@echo "Running Task Service tests..."
	@cd task_service && python test_service.py
