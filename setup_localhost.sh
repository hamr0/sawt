#!/bin/bash

# Arabic TTS - Localhost Setup Script
# This script sets up the Arabic TTS system for localhost development

echo "================================================"
echo "Arabic TTS System - Localhost Setup"
echo "================================================"
echo ""

# Check if running from correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the ArabicTTS directory"
    exit 1
fi

echo "✓ Running from correct directory"
echo ""

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi
echo ""

# Check required files
echo "Checking project files..."
REQUIRED_FILES=("app.py" "src/main.py" "data/dictionaries/masterTTS.json" "templates/index.html" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done
echo ""

# Check if dependencies are installed
echo "Checking Python dependencies..."
if python3 -c "import flask" 2>/dev/null; then
    echo "✓ Dependencies already installed"
else
    echo "⚠️  Dependencies not installed"
    echo ""
    read -p "Install dependencies now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing dependencies..."
        pip3 install --user -r requirements.txt
        if [ $? -eq 0 ]; then
            echo "✓ Dependencies installed successfully"
        else
            echo "❌ Failed to install dependencies"
            exit 1
        fi
    else
        echo "⚠️  Skipping dependency installation"
        echo "   You can install later with: pip3 install -r requirements.txt"
    fi
fi
echo ""

# Test imports
echo "Testing Python imports..."
python3 -c "
from src.main import ArabicTTS
import flask
print('✓ All imports successful')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ All imports successful"
else
    echo "❌ Import test failed. Please check dependencies."
    exit 1
fi
echo ""

# Test basic functionality
echo "Testing basic functionality..."
python3 -c "
from src.main import ArabicTTS
tts = ArabicTTS('MSA')
result = tts.process_text('مرحبا')
print('✓ Text processing works')
print(f'  Dialect: {result[\"dialect\"]}')
print(f'  Processed: {len(result[\"words\"])} word(s)')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
else
    echo "❌ Processing test failed"
    exit 1
fi
echo ""

# Check port availability
echo "Checking port 5000..."
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 5000 is already in use"
    echo "   You may need to stop the existing process or use a different port"
else
    echo "✓ Port 5000 is available"
fi
echo ""

# Summary
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "📚 Documentation Available:"
echo "  - PROJECT_DOCUMENTATION.md  (Comprehensive guide)"
echo "  - LOCALHOST_SETUP_GUIDE.md  (Detailed setup instructions)"
echo "  - README.md                  (Quick reference)"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "  1. Start the web application:"
echo "     python3 app.py"
echo ""
echo "  2. Open browser to:"
echo "     http://localhost:5000"
echo ""
echo "  3. Or use Python API:"
echo "     python3 -c \"from src.main import ArabicTTS; tts=ArabicTTS('MSA'); print(tts.process_text('السلام عليكم'))\""
echo ""
echo "📝 Supported Dialects:"
echo "  - MSA        (Modern Standard Arabic)"
echo "  - EG         (Egyptian Arabic)"
echo "  - Gulf       (Gulf Arabic)"
echo "  - Levantine (Levantine Arabic)"
echo "  - Maghreb    (Maghrebi Arabic)"
echo ""
echo "🧪 Run Tests:"
echo "  python3 -m pytest tests/ -v"
echo ""
echo "================================================"
echo "✓ Ready to process Arabic text!"
echo "================================================"
