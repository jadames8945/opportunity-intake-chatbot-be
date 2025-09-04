.PHONY: format lint test install

# Format code using Black and isort
format:
	@echo "🎨 Formatting code..."
	@poetry run black . --line-length 88
	@poetry run isort . --profile black --line-length 88
	@echo "✅ Formatting complete!"

# Run linting
lint:
	@echo "🔍 Running linters..."
	@poetry run flake8 . --max-line-length=88 --extend-ignore=E203,W503,E501,W293,W291,F841,F541,F401,E402

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@poetry install --with dev

# Run tests
test:
	@echo "🧪 Running tests..."
	@poetry run python -m pytest tests/ -v

# Setup pre-commit hooks
setup-hooks:
	@echo "🔧 Setting up pre-commit hooks..."
	@poetry run pre-commit install

# Run pre-commit on all files
pre-commit:
	@echo "🔍 Running pre-commit on all files..."
	@poetry run pre-commit run --all-files

# Clean up Python cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Cleanup complete!"

# Show help
help:
	@echo "Available commands:"
	@echo "  format       - Format code using Black and isort"
	@echo "  lint         - Run linting with flake8"
	@echo "  test         - Run tests"
	@echo "  install      - Install dependencies"
	@echo "  setup-hooks  - Setup pre-commit hooks"
	@echo "  pre-commit   - Run pre-commit on all files"
	@echo "  clean        - Clean up cache files"
	@echo "  help         - Show this help message"
