.PHONY: help install dev test lint format migrate seed clean docker-build docker-run

help:
	@echo "DevOps Release Manager - Backend Development"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Run development server"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linting"
	@echo "  make format        - Format code with black and isort"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-new   - Create new migration (use MSG='description')"
	@echo "  make seed          - Seed database with test data"
	@echo "  make clean         - Clean temporary files"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"

install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint:
	flake8 app
	mypy app
	isort --check-only app

format:
	black .
	isort .

migrate:
	alembic upgrade head

migrate-new:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide migration message with MSG='your message'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MSG)"

migrate-rollback:
	alembic downgrade -1

seed:
	python scripts/seed_db.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

docker-build:
	docker build -t release-manager:latest .

docker-run:
	docker run -d \
		--name release-manager \
		-p 8000:8000 \
		--env-file .env \
		release-manager:latest

docker-stop:
	docker stop release-manager
	docker rm release-manager

docker-logs:
	docker logs -f release-manager
