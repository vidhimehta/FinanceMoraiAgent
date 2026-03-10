#!/bin/bash
# Installation script for FinanceMoraiAgent

echo "========================================="
echo "FinanceMoraiAgent Installation"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Create storage directories
echo ""
echo "Creating storage directories..."
mkdir -p storage/cache storage/historical storage/models storage/results

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
fi

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python src/main.py"
echo ""
echo "To run tests:"
echo "  pytest tests/"
echo ""
