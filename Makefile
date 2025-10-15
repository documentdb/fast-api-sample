.PHONY: help build up down logs shell test clean format lint

help:
	@echo "FastAPI + DocumentDB E-commerce Demo - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build    - Build Docker containers"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View container logs"
	@echo "  make shell    - Open a shell in the backend container"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make format   - Format code with black and isort"
	@echo "  make lint     - Run linting checks"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started! API docs available at http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec backend /bin/bash

test:
	docker-compose exec backend pytest -v

clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/tests/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format:
	docker-compose exec backend black backend/app backend/tests
	docker-compose exec backend isort backend/app backend/tests

lint:
	docker-compose exec backend black --check backend/app backend/tests
	docker-compose exec backend isort --check-only backend/app backend/tests
	docker-compose exec backend mypy backend/app
