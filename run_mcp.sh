#!/bin/bash

# MCP Server Runner Script
# This script ensures the virtual environment is activated before running the MCP server

echo "🔌 Starting Email Assistant MCP Server..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "mcp_server.py" ]; then
    echo "❌ Error: mcp_server.py not found. Please run this script from the email-assistant directory."
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
    echo "   The MCP server will prompt for it if needed"
else
    echo "✅ GEMINI_API_KEY is configured"
fi

# Run the MCP server
echo "🔌 Starting MCP server..."
python mcp_server.py
