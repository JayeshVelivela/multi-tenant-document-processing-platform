.PHONY: help build up down logs test migrate seed clean

help:
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs from all services"
	@echo "  make test       - Run tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make seed       - Seed database with sample data"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make shell-api  - Open shell in API container"
	@echo "  make shell-db   - Open PostgreSQL shell"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@make migrate

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec api pytest -v --cov=app --cov-report=term-missing

migrate:
	docker-compose exec api alembic upgrade head

migrate-create:
	docker-compose exec api alembic revision --autogenerate -m "$(name)"

seed:
	docker-compose exec api python scripts/seed_data.py

clean:
	docker-compose down -v
	docker system prune -f

shell-api:
	docker-compose exec api /bin/bash

shell-db:
	docker-compose exec postgres psql -U postgres -d document_platform

