#!/usr/bin/env python3
"""Code formatting script using Black and isort."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    """Main formatting function."""
    print("🎨 Starting code formatting...")

    # Get the project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent

    # Change to project root
    import os

    os.chdir(project_root)

    # Run Black
    black_success = run_command(
        "poetry run black . --line-length 88", "Black formatter"
    )

    # Run isort
    isort_success = run_command(
        "poetry run isort . --profile black --line-length 88", "isort import sorter"
    )

    if black_success and isort_success:
        print("🎉 All formatting completed successfully!")
        return 0
    else:
        print("💥 Some formatting steps failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
