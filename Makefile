# Makefile for Universal Intelligent Communicator (UnIC)
# Provides easy commands for common development tasks

.PHONY: help install test run demo clean lint format setup api interactive web

# Default target
help:
	@echo "UnIC - Universal Intelligent Communicator"
	@echo "=========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install all dependencies and setup the system"
	@echo "  setup       - Setup the system (create directories, initialize DB)"
	@echo "  test        - Run all tests"
	@echo "  run         - Start UnIC in interactive mode"
	@echo "  api         - Start UnIC API server"
	@echo "  web         - Start API server and open web interface"
	@echo "  demo        - Run comprehensive demo"
	@echo "  clean       - Clean up temporary files and caches"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black"
	@echo "  docs        - Generate documentation"
	@echo "  package     - Create distribution package"
	@echo ""

# Installation
install:
	@echo "Installing UnIC..."
	python install.py

setup:
	@echo "Setting up UnIC..."
	@mkdir -p data_lake logs models temp
	@echo "Directories created"
	@python -c "from core.database import db_manager; print('Database initialized')"
	@echo "Setup complete!"

# Testing
test:
	@echo "Running UnIC tests..."
	python test_unic.py

# Running the system
run:
	@echo "Starting UnIC in interactive mode..."
	python main.py --mode interactive

api:
	@echo "Starting UnIC API server..."
	python main.py --mode api

web:
	@echo "Starting UnIC web interface..."
	@echo "Starting API server in background..."
	@python main.py --mode api &
	@sleep 3
	@echo "Opening web interface..."
	@if command -v open >/dev/null 2>&1; then \
		open web_interface/index.html; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open web_interface/index.html; \
	else \
		echo "Please open web_interface/index.html in your browser"; \
	fi
	@echo "API server running on http://localhost:5000"
	@echo "Web interface should open automatically"

# Demo
demo:
	@echo "Running UnIC demo..."
	python demo.py

# Data ingestion
ingest:
	@echo "Running data ingestion..."
	python main.py --mode ingest --source all

ingest-arxiv:
	@echo "Ingesting ArXiv papers..."
	python main.py --mode ingest --source arxiv

ingest-quotes:
	@echo "Ingesting quotes..."
	python main.py --mode ingest --source quotes

# Development tools
clean:
	@echo "Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Cleanup complete!"

lint:
	@echo "Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 . --max-line-length=100 --ignore=E501,W503; \
	else \
		echo "flake8 not found. Install with: pip install flake8"; \
	fi

format:
	@echo "Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black . --line-length=100; \
	else \
		echo "black not found. Install with: pip install black"; \
	fi

# Documentation
docs:
	@echo "Generating documentation..."
	@if command -v pydoc >/dev/null 2>&1; then \
		mkdir -p docs; \
		pydoc -w core/*.py ingestion/*.py api/*.py; \
		mv *.html docs/; \
		echo "Documentation generated in docs/"; \
	else \
		echo "pydoc not available"; \
	fi

# Packaging
package:
	@echo "Creating distribution package..."
	python setup.py sdist bdist_wheel
	@echo "Package created in dist/"

# Development environment
dev-setup:
	@echo "Setting up development environment..."
	pip install -r requirements.txt
	pip install -e .
	pip install black flake8 mypy pytest
	@echo "Development environment ready!"

# Database operations
db-reset:
	@echo "Resetting database..."
	@rm -f data_lake/unic_database.db
	@python -c "from core.database import db_manager; print('Database reset')"
	@echo "Database reset complete!"

db-stats:
	@echo "Database statistics:"
	@python -c "from core.database import db_manager; import json; print(json.dumps(db_manager.get_statistics(), indent=2))"

# Performance testing
perf-test:
	@echo "Running performance tests..."
	@python -c "
import time
from core.nlp_engine import nlp_engine
from core.database import db_manager

# Test embedding generation speed
start = time.time()
for i in range(100):
    nlp_engine.get_embedding(f'Test sentence number {i}')
end = time.time()
print(f'Embedding generation: {(end-start)/100:.4f}s per sentence')

# Test database operations
start = time.time()
for i in range(100):
    db_manager.get_knowledge_entries(limit=10)
end = time.time()
print(f'Database queries: {(end-start)/100:.4f}s per query')
"

# System information
info:
	@echo "UnIC System Information"
	@echo "======================"
	@python -c "
import sys
import platform
from pathlib import Path

print(f'Python version: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Project root: {Path.cwd()}')
print(f'Python executable: {sys.executable}')

try:
    from core.database import db_manager
    stats = db_manager.get_statistics()
    print(f'Database entries: {stats[\"total_knowledge_entries\"]}')
    print(f'Conversations: {stats[\"total_conversations\"]}')
except Exception as e:
    print(f'Database error: {e}')
"

# Quick start
quick-start: setup run

# Full setup
full-setup: install setup ingest

# Development workflow
dev: dev-setup test lint format

# Production setup
prod: install setup test 