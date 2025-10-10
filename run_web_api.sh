#!/bin/bash

# Web API Runner Script
# This script runs the email assistant as a web API

echo "🌐 Starting Email Assistant Web API..."
echo "====================================="

# Check if we're in the right directory
if [ ! -f "web_api.py" ]; then
    echo "❌ Error: web_api.py not found. Please run this script from the email-assistant directory."
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
    echo "   The API will prompt for it if needed"
else
    echo "✅ GEMINI_API_KEY is configured"
fi

# Install Flask if not already installed
echo "📦 Checking Flask installation..."
pip install flask > /dev/null 2>&1

# Run the web API
echo "🌐 Starting web API server..."
echo "📡 API will be available at: http://localhost:5000"
echo "📋 Available endpoints:"
echo "   POST /api/process-emails"
echo "   POST /api/analyze-email"
echo "   POST /api/generate-reply"
echo "   GET /api/health"
echo "   GET /api/capabilities"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python web_api.py
