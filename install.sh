#!/bin/bash

# Installation script for Visa Checker Bot

echo "╔════════════════════════════════════════════════╗"
echo "║  🤖 Visa Checker Bot - Installation Script    ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "💾 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✅ Virtual environment created"
echo ""

# Install requirements
echo "📥 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Requirements installed"
echo ""

# Setup .env
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Telegram Bot Token and User ID"
    echo ""
fi

# Run tests
echo "🧪 Running tests..."
python3 test.py
echo ""

echo "╔════════════════════════════════════════════════╗"
echo "║  ✅ Installation Complete! ✅                 ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env with your Telegram Bot Token"
echo "   2. Run: python3 bot.py"
echo ""
