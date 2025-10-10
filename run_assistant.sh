#!/bin/bash

# Email Assistant Runner Script
# This script ensures the virtual environment is activated before running

echo "🤖 Starting AI Email Assistant..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "email_assistant.py" ]; then
    echo "❌ Error: email_assistant.py not found. Please run this script from the email-assistant directory."
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
    echo "   The assistant will prompt for it if needed"
else
    echo "✅ GEMINI_API_KEY is configured"
fi

# Run the email assistant
echo "📧 Running email assistant..."
python email_assistant.py

echo "✅ Email assistant finished"
