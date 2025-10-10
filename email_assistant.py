#!/usr/bin/env python3
"""
AI Email Assistant - Intelligent email processing with Gemini AI
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.generativeai as genai
import base64
from email.mime.text import MIMEText

# Import the new AI assistant system
from ai_assistant import ai_assistant

# Gemini API key prompt if not found
def get_gemini_api_key():
    """Prompt user for Gemini API key if not found in environment."""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("🔑 Gemini API Key Required")
        print("=" * 50)
        print("To use the AI email assistant, you need a Gemini API key.")
        print("Get your key from: https://aistudio.google.com/")
        print()
        
        while True:
            api_key = input("Enter your Gemini API key: ").strip()
            
            if api_key and api_key.startswith("AIza"):
                # Set for current session
                os.environ["GEMINI_API_KEY"] = api_key
                print("✅ API key set successfully!")
                print()
                return api_key
            else:
                print("❌ Invalid API key format. Gemini keys start with 'AIza'")
                print("Please try again or visit https://aistudio.google.com/ to get your key.")
                print()
    
    return api_key

# Get Gemini API key
GEMINI_API_KEY = get_gemini_api_key()

# Initialize AI assistant with API key
ai_assistant.initialize_gemini(GEMINI_API_KEY)

# --- CONFIGURATION ---
CONTACTS = {
    "sales": "ads.al@laposte.net",
    "support": "victor.sana@berkeley.edu", 
    "technical": "idris.houiralami@berkeley.edu",
}

# Gemini Configuration
GEMINI_MODEL = 'gemini-2.0-flash'  # Gemini Flash model

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Get authenticated Gmail service."""
    creds = None
    
    # Check if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, body, in_reply_to=None, references=None):
    """Create a message for an email."""
    message = MIMEText(body)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
    if references:
        message['References'] = references
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        return message
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def generate_smart_reply(sender_name, subject, body, classification):
    """Generate smart replies based on email content."""
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # Thank you responses
    if any(word in subject_lower + body_lower for word in ['thank', 'thanks', 'appreciate', 'grateful']):
        return f"Hi {sender_name},\n\nYou're very welcome! I'm glad I could help.\n\nBest regards,\nJohn"
    
    # Urgent requests
    if any(word in subject_lower + body_lower for word in ['urgent', 'asap', 'emergency', 'critical']):
        return f"Hi {sender_name},\n\nI've received your urgent request and will prioritize it immediately. I'll get back to you as soon as possible.\n\nBest regards,\nJohn"
    
    # General questions/requests
    if any(word in subject_lower + body_lower for word in ['can you', 'please', 'send me', 'email', 'address', 'contact', 'manager']):
        return f"Hi {sender_name},\n\nThank you for your message. I'll forward this to the appropriate team member who can best assist you.\n\nBest regards,\nJohn"
    
    # Help requests
    if any(word in subject_lower + body_lower for word in ['help', 'support', 'issue', 'problem']):
        return f"Hi {sender_name},\n\nI understand you need assistance. I'll connect you with our support team who will be able to help you effectively.\n\nBest regards,\nJohn"
    
    # Default response
    return f"Hi {sender_name},\n\nThank you for your email. I've received your message and will ensure it gets the appropriate attention.\n\nBest regards,\nJohn"

def process_emails():
    """Main function to fetch, analyze, and process emails."""
    
    try:
        service = get_gmail_service()
    except Exception as e:
        print(f"ERROR: Failed to authenticate with Gmail. Check credentials.json and ensure it's a 'Desktop App'. Details: {e}")
        return

    # Initialize Gemini AI
    print("Connected to Gmail and Gemini AI. Starting email processing...")
    
    # --- MAIN LOGIC ---
    user_id = 'me'
    
    try:
        # Get unread messages
        results = service.users().messages().list(userId=user_id, labelIds=['UNREAD']).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No unread messages found.")
            return
        
        print(f"Found {len(messages)} unread messages to process.")
        
        for message in messages:
            msg_id = message['id']
            
            # Get message details
            msg = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
            # Extract headers
            headers = msg['payload'].get('headers', [])
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), '')
            
            # Extract sender email
            sender_email = sender.split('<')[-1].split('>')[0] if '<' in sender else sender
            
            # Extract body
            body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                data = msg['payload']['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            print(f"\nProcessing email (ID: {msg_id}) from {sender} with Subject: '{subject[:50]}...'")

            # AI Analysis
            try:
                # Use the AI assistant for intelligent analysis
                intent_analysis = ai_assistant.analyze_email_intent(sender, subject, body, sender_email)
                
                # Extract analysis results
                classification = intent_analysis["intent"]["category"]
                action = intent_analysis["intent"]["action"]
                reply_needed = intent_analysis["intent"]["requires_reply"]
                urgency = intent_analysis["intent"]["urgency"]
                reasoning = intent_analysis["reasoning"]
                
                print(f"  -> AI Analysis: {classification} | Action: {action} | Urgency: {urgency}")
                print(f"  -> Reasoning: {reasoning}")
                
            except Exception as e:
                print(f"  -> AI analysis failed: {e}")
                print(f"  -> Using rule-based fallback classification...")
                
                # Rule-based fallback classification
                subject_lower = subject.lower()
                body_lower = body.lower()
                
                # Simple keyword-based classification with reply detection
                if any(word in subject_lower + body_lower for word in ['sales', 'buy', 'purchase', 'price', 'cost', 'quote', 'order']):
                    classification = 'sales'
                    action = 'forward'
                    reply_needed = False
                    urgency = 'medium'
                    reasoning = 'Rule-based: Contains sales-related keywords'
                elif any(word in subject_lower + body_lower for word in ['help', 'support', 'issue', 'problem', 'bug', 'error', 'fix']):
                    classification = 'support'
                    action = 'forward'
                    reply_needed = False
                    urgency = 'medium'
                    reasoning = 'Rule-based: Contains support-related keywords'
                elif any(word in subject_lower + body_lower for word in ['technical', 'api', 'integration', 'code', 'development']):
                    classification = 'technical'
                    action = 'forward'
                    reply_needed = False
                    urgency = 'medium'
                    reasoning = 'Rule-based: Contains technical keywords'
                elif any(word in subject_lower + body_lower for word in ['urgent', 'asap', 'emergency', 'critical']):
                    classification = 'executive'
                    action = 'forward'
                    reply_needed = False
                    urgency = 'high'
                    reasoning = 'Rule-based: Contains urgent keywords'
                elif any(word in subject_lower + body_lower for word in ['thank', 'thanks', 'appreciate', 'grateful']):
                    classification = 'other'
                    action = 'reply'
                    reply_needed = True
                    urgency = 'low'
                    reasoning = 'Rule-based: Thank you message'
                elif any(word in subject_lower + body_lower for word in ['question', 'ask', 'can you', 'could you', 'please', '?']):
                    classification = 'support'
                    action = 'reply'
                    reply_needed = True
                    urgency = 'medium'
                    reasoning = 'Rule-based: Contains question/request keywords'
                else:
                    classification = 'support'
                    action = 'forward'
                    reply_needed = False
                    urgency = 'low'
                    reasoning = 'Rule-based: Default classification to support'
                
                print(f"  -> Fallback Analysis: {classification} | Action: {action} | Urgency: {urgency}")
                print(f"  -> Reasoning: {reasoning}")

            # Process based on analysis
            if reply_needed:
                try:
                    # Generate intelligent reply
                    reply_text = ai_assistant.generate_intelligent_reply(sender, subject, body, sender_email)
                    
                    # Send reply
                    reply_message = create_message(
                        sender="johnweakagent@gmail.com",
                        to=sender_email,
                        subject=f"Re: {subject}",
                        body=reply_text,
                        in_reply_to=message_id,
                        references=message_id
                    )
                    
                    send_message(service, user_id, reply_message)
                    print(f"  -> ✅ Reply sent successfully")
                    
                except Exception as e:
                    print(f"  -> ❌ Failed to send reply: {e}")
                    # Fallback to rule-based reply
                    reply_text = generate_smart_reply(sender.split('<')[0].strip(), subject, body, classification)
                    reply_message = create_message(
                        sender="johnweakagent@gmail.com",
                        to=sender_email,
                        subject=f"Re: {subject}",
                        body=reply_text,
                        in_reply_to=message_id,
                        references=message_id
                    )
                    send_message(service, user_id, reply_message)
                    print(f"  -> ✅ Fallback reply sent successfully")

            # Forward if needed
            if action in ['forward', 'both']:
                try:
                    # Get forwarding recipient
                    forward_to = ai_assistant.get_forwarding_recipient(intent_analysis if 'intent_analysis' in locals() else None)
                    
                    if forward_to:
                        # Create forwarded message
                        forward_body = f"""
--- FORWARDED EMAIL ---
Urgency: {urgency}
AI Analysis: {reasoning}

Original Email:
From: {sender}
Subject: {subject}

{body}

---
Forwarded by AI Email Assistant
"""
                        
                        forward_message = create_message(
                            sender="johnweakagent@gmail.com",
                            to=forward_to,
                            subject=f"FWD: {subject}",
                            body=forward_body
                        )
                        
                        send_message(service, user_id, forward_message)
                        print(f"  -> ✅ Email forwarded to {forward_to}")
                    else:
                        print(f"  -> ⚠️ No forwarding recipient determined")
                        
                except Exception as e:
                    print(f"  -> ❌ Failed to forward email: {e}")

            # Mark as read
            service.users().messages().modify(
                userId=user_id, 
                id=msg_id, 
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            print(f"  -> ✅ Email marked as read")

    except Exception as e:
        print(f"Error processing emails: {e}")

if __name__ == "__main__":
    process_emails()
