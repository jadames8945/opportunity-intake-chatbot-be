#!/bin/bash

echo "Running Black formatter..."
poetry run black . --line-length 88
poetry run black ../auth --line-length 88
poetry run black ../common --line-length 88
poetry run black ../worker --line-length 88

echo "Running isort..."
poetry run isort . --profile black --line-length 88
poetry run isort ../auth --profile black --line-length 88
poetry run isort ../common --profile black --line-length 88
poetry run isort ../worker --profile black --line-length 88

echo "Formatting complete!"
