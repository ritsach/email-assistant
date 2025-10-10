#!/usr/bin/env python3
"""
Gemini Integration for Email Assistant
This allows Gemini to interact with your email assistant through API calls
"""

import os
import json
import google.generativeai as genai
from email_assistant import process_emails, get_gmail_service
from ai_assistant import ai_assistant

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

class EmailAssistantAPI:
    """API wrapper for email assistant functionality"""
    
    def __init__(self):
        self.ai_assistant = ai_assistant
        self.ai_assistant.initialize_gemini(os.environ.get("GEMINI_API_KEY"))
    
    def process_emails(self):
        """Process unread emails"""
        try:
            process_emails()
            return {"status": "success", "message": "Emails processed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def analyze_email(self, sender, subject, body):
        """Analyze a specific email"""
        try:
            intent_analysis = self.ai_assistant.analyze_email_intent(sender, subject, body)
            return {"status": "success", "analysis": intent_analysis}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_reply(self, sender, subject, body):
        """Generate a reply for an email"""
        try:
            reply = self.ai_assistant.generate_intelligent_reply(sender, subject, body)
            return {"status": "success", "reply": reply}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def create_gemini_prompt(user_query):
    """Create a prompt for Gemini to understand email assistant capabilities"""
    
    system_prompt = """You are an AI assistant that can help with email management. You have access to an email assistant with the following capabilities:

1. **Process Emails**: Automatically process unread emails, classify them, and take appropriate actions
2. **Analyze Email**: Analyze email content to determine intent, urgency, and required actions
3. **Generate Replies**: Create intelligent, contextual replies to emails
4. **Forward Emails**: Forward emails to appropriate team members based on content

Available functions:
- `process_emails()`: Process all unread emails
- `analyze_email(sender, subject, body)`: Analyze a specific email
- `generate_reply(sender, subject, body)`: Generate a reply for an email

When the user asks about email management, you can call these functions to help them.
"""
    
    return f"{system_prompt}\n\nUser query: {user_query}"

def main():
    """Main function to handle Gemini interactions"""
    
    print("🤖 Gemini Email Assistant Integration")
    print("=" * 50)
    
    # Initialize email assistant API
    email_api = EmailAssistantAPI()
    
    while True:
        try:
            user_input = input("\n💬 Ask me about email management (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Create prompt for Gemini
            prompt = create_gemini_prompt(user_input)
            
            # Get response from Gemini
            response = model.generate_content(prompt)
            gemini_response = response.text
            
            print(f"\n🤖 Gemini Response:\n{gemini_response}")
            
            # Check if Gemini suggests using email functions
            if any(keyword in gemini_response.lower() for keyword in ['process emails', 'analyze email', 'generate reply']):
                if 'process emails' in gemini_response.lower():
                    print("\n📧 Processing emails...")
                    result = email_api.process_emails()
                    print(f"Result: {result['message']}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
