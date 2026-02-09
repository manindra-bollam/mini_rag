.PHONY: help install setup test lint format clean build query ui sample-data

help:
	@echo "Mini-RAG Makefile Commands:"
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Run setup script"
	@echo "  make sample-data  - Generate sample PDF files"
	@echo "  make build        - Build the RAG index"
	@echo "  make query        - Run a sample query"
	@echo "  make ui           - Launch Streamlit UI"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean generated files"
	@echo "  make evaluate     - Run evaluation"

install:
	pip install -r requirements.txt

setup:
	bash setup.sh

sample-data:
	pip install reportlab
	python create_sample_pdfs.py

build:
	python rag.py --build

query:
	python rag.py --query "Which sensors support 1200°C?"

query-json:
	python rag.py --query "temperature sensors" --json

ui:
	streamlit run app.py

test:
	pytest -v

test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src tests --max-line-length=100
	mypy src

format:
	black src tests *.py

format-check:
	black --check src tests *.py

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -rf .pytest_cache .mypy_cache htmlcov
	rm -rf *.egg-info dist build
	rm -f results.json
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean
	rm -rf index/
	rm -rf venv/

evaluate:
	python evaluate.py

# Development workflow
dev-setup: install sample-data build
	@echo ""
	@echo "Development environment ready!"
	@echo "Try: make query"

# CI/CD simulation
ci: lint test
	@echo ""
	@echo "CI checks passed!"