#!/bin/bash
# Setup script for environment variables

echo "🔧 Setting up environment variables for Email Assistant"
echo "=================================================="

# Check if GEMINI_API_KEY is already set
if [ -n "$GEMINI_API_KEY" ]; then
    echo "✅ GEMINI_API_KEY is already set"
else
    echo "❌ GEMINI_API_KEY is not set"
    echo ""
    echo "To set your Gemini API key:"
    echo "1. Get your API key from: https://aistudio.google.com/"
    echo "2. Run: export GEMINI_API_KEY='YOUR-API-KEY'"
    echo "3. Or add to ~/.zshrc: echo 'export GEMINI_API_KEY=\"your-key\"' >> ~/.zshrc"
    echo ""
fi

# Check if credentials.json exists
if [ -f "credentials.json" ]; then
    echo "✅ credentials.json found"
else
    echo "❌ credentials.json not found"
    echo ""
    echo "To set up Gmail API:"
    echo "1. Go to Google Cloud Console"
    echo "2. Enable Gmail API"
    echo "3. Create OAuth 2.0 credentials"
    echo "4. Download credentials.json to this directory"
    echo ""
fi

echo "=================================================="
echo "Setup complete! Run 'python standalone_assistant.py' to test."
