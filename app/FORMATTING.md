# Code Formatting

This project uses Black and isort for code formatting, with pre-commit hooks to ensure consistent code style across all backend directories.

## Tools Used

- **Black**: Python code formatter
- **isort**: Import sorting
- **pre-commit**: Git hooks for automated formatting

## Directories Formatted

The formatting tools are applied to all Python files in:
- `app/` - Main application code
- `auth/` - Authentication service
- `common/` - Shared utilities and infrastructure
- `worker/` - Celery worker tasks

## Running Formatting

### Manual Formatting
```bash
# Run the formatting script (formats all directories)
./format_code.sh

# Or use Make
make format

# Or run individual tools on specific directories
poetry run black ../auth --line-length 88
poetry run isort ../auth --profile black --line-length 88
```

### Pre-commit Hooks
Pre-commit hooks are automatically installed and will run on every commit. To run manually:

```bash
poetry run pre-commit run --all-files
```

## Configuration

- **Line length**: 88 characters
- **Black profile**: Used for isort compatibility
- **Pre-commit**: Automatically formats staged files
- **Scope**: All Python files in app/, auth/, common/, and worker/ directories

## Installation

The formatting tools are installed as development dependencies:

```bash
poetry install --with dev
```

Pre-commit hooks are installed automatically when you run:

```bash
poetry run pre-commit install
```

## Available Commands

```bash
make help          # Show all available commands
make format        # Format all code
make lint          # Run linting
make clean         # Clean cache files
make pre-commit    # Run pre-commit on all files
```
