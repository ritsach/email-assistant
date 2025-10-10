#!/usr/bin/env python3
"""
Standalone Email Assistant - Original Functionality
This preserves the original email assistant functionality without MCP
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from email_assistant import process_emails, get_gmail_service

def main():
    """Run the original email assistant functionality."""
    print("🤖 AI Email Assistant - Standalone Mode")
    print("=" * 50)
    
    try:
        # Check Gmail service connection
        service = get_gmail_service()
        print("✅ Connected to Gmail successfully")
        
        # Process emails
        print("\n📧 Processing emails...")
        process_emails()
        
        print("\n✅ Email processing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
