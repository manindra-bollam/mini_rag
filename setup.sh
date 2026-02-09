#!/bin/bash

# Mini-RAG Setup Script
# This script sets up the Mini-RAG environment and creates sample data

set -e  # Exit on error

echo "=========================================="
echo "Mini-RAG Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "Error: Python 3.10 or higher is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo ""
echo "Creating directories..."
mkdir -p data index

# Ask about sample PDFs
echo ""
read -p "Do you want to generate sample PDF files? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing reportlab for PDF generation..."
    pip install reportlab
    echo ""
    echo "Generating sample PDFs..."
    python create_sample_pdfs.py
fi

# Success message
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Build the index:"
echo "   python rag.py --build"
echo ""
echo "3. Query the system:"
echo "   python rag.py --query \"Which sensors support 1200°C?\""
echo ""
echo "4. Or launch the Streamlit UI:"
echo "   streamlit run app.py"
echo ""