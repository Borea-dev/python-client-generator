#!/bin/bash

# Exit on error
set -e

# Function to print usage
print_usage() {
    echo "Usage: ./setup.sh [OPTIONS]"
    echo "Options:"
    echo "  -r, --recreate    Recreate virtual environment (deletes existing .venv)"
    echo "  -i, --reinstall   Reinstall all requirements"
    echo "  -h, --help        Show this help message"
}

# Parse command line arguments
RECREATE=false
REINSTALL=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -r|--recreate) RECREATE=true ;;
        -i|--reinstall) REINSTALL=true ;;
        -h|--help) print_usage; exit 0 ;;
        *) echo "Unknown parameter: $1"; print_usage; exit 1 ;;
    esac
    shift
done

echo "Setting up Python virtual environment..."

# Handle recreation of virtual environment if requested
if [ "$RECREATE" = true ] && [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Install or reinstall dependencies
if [ "$REINSTALL" = true ]; then
    echo "Reinstalling all dependencies..."
    pip install --force-reinstall .
    echo "Dependencies reinstalled successfully"
elif [ -f "pyproject.toml" ]; then
    pip install -e .
    echo "Dependencies installed successfully"
else
    echo "Error: pyproject.toml not found"
    exit 1
fi

echo "Setup complete! Virtual environment is activated."
echo "To deactivate the virtual environment, run: deactivate"
