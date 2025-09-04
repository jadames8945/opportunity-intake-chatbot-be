# Code Formatting

This project uses Black and isort for code formatting, with pre-commit hooks to ensure consistent code style.

## Tools Used

- **Black**: Python code formatter
- **isort**: Import sorting
- **pre-commit**: Git hooks for automated formatting

## Running Formatting

### Manual Formatting
```bash
# Run the formatting script
./format_code.sh

# Or run individual tools
poetry run black . --line-length 88
poetry run isort . --profile black --line-length 88
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

## Installation

The formatting tools are installed as development dependencies:

```bash
poetry install --with dev
```

Pre-commit hooks are installed automatically when you run:

```bash
poetry run pre-commit install
```
