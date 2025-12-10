#!/bin/bash
# Setup script for Unix-like systems (Linux, Mac)

echo "=================================="
echo "Workflow Engine Setup"
echo "=================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Start the server: python -m uvicorn app.main:app --reload"
echo "  3. Visit: http://localhost:8000/docs"
echo ""
