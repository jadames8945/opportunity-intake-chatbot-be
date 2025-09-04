#!/bin/bash

echo "Running Black formatter..."
poetry run black . --line-length 88

echo "Running isort..."
poetry run isort . --profile black --line-length 88

echo "Formatting complete!"
