#!/bin/bash

# Gemini Integration Runner Script
# This script runs the direct Gemini integration

echo "🤖 Starting Gemini Email Assistant Integration..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "gemini_integration.py" ]; then
    echo "❌ Error: gemini_integration.py not found. Please run this script from the email-assistant directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set in environment"
    echo "   The integration will prompt for it if needed"
else
    echo "✅ GEMINI_API_KEY is configured"
fi

# Run the Gemini integration
echo "🤖 Starting Gemini integration..."
python gemini_integration.py
