#!/usr/bin/env python3
"""
Real-time Email Monitor - Automatically processes new emails
"""

import os
import time
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import anthropic
import boto3
import base64
from email.mime.text import MIMEText

# Set Bedrock API key in environment variable
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "ABSKQmVkcm9ja0FQSUtleS03bXZoLWF0LTY2OTQ0NjEwMTEyNjpTZ2ZVK3FSMWJYR1BQcE54OENmY0RIWXhWRWJLelJJYUJnMVhFRXN1WGg0MmVFRWwzUWpBcjRqakxJZz0="

# Configuration
CONTACTS = {
    "sales": "ads.al@laposte.net",
    "support": "victor.sana@berkeley.edu", 
    "technical": "idris.houiralami@berkeley.edu",
}

AWS_REGION = 'us-east-1'
BEDROCK_MODEL_ID = 'us.anthropic.claude-sonnet-4-20250514-v1:0'

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_gmail_service():
    """Handles authentication and returns the Gmail service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_message_body(message):
    """Parses a Gmail message object to extract the plain text body."""
    msg_parts = message.get('payload', {}).get('parts', [])
    
    for part in msg_parts:
        if part['mimeType'] == 'text/plain':
            data = part['body'].get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')

    data = message.get('payload', {}).get('body', {}).get('data')
    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8')
    
    return ""

def create_message(sender, to, subject, message_text, in_reply_to=None, references=None):
    """Creates an email message to be sent via the Gmail API."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
    if references:
        message['References'] = references
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Sends the message via the Gmail API."""
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print(f"  -> Successfully sent reply/forward (ID: {message['id']})")
        return message
    except Exception as error:
        print(f"  -> An error occurred while sending: {error}")
        return None

def generate_smart_reply(sender, subject, body):
    """Generate intelligent, human-like replies based on email content."""
    
    # Extract sender name
    sender_name = sender.split('<')[0].strip() if '<' in sender else sender.split('@')[0]
    
    # Analyze the email content for context
    body_lower = body.lower()
    subject_lower = subject.lower() if subject else ""
    
    # Determine the type of request (order matters - more specific first)
    if any(word in body_lower for word in ['thank', 'thanks', 'appreciate', 'grateful']):
        return f"""Hi {sender_name},

You're very welcome! It's always great to hear positive feedback.

I'm glad we could help, and I'll make sure to share your kind words with the team.

If there's anything else we can do for you, please don't hesitate to reach out.

Best regards,
John"""

    elif any(word in body_lower for word in ['urgent', 'asap', 'immediately', 'emergency']):
        return f"""Hello {sender_name},

I understand this is urgent, and I want to make sure we address it promptly.

I'm immediately forwarding your message to our priority support team who will respond within 2 hours. For immediate assistance, please also call our emergency line: +1 (555) 911-HELP

I'll personally follow up to ensure this gets the attention it deserves.

Best regards,
John"""

    elif any(word in body_lower for word in ['complaint', 'issue', 'problem', 'disappointed', 'angry']):
        return f"""Hello {sender_name},

I'm sorry to hear about your experience, and I truly appreciate you taking the time to reach out.

I want to make sure we address your concerns properly. I'm forwarding your message to our customer success team who will personally review your case and work to resolve this matter.

They'll be in touch within 24 hours to discuss this further and find a solution that works for you.

Thank you for your patience, and I apologize for any inconvenience.

Best regards,
John"""

    elif any(word in body_lower for word in ['manager', 'supervisor', 'boss', 'director']):
        if any(word in body_lower for word in ['email', 'address', 'contact']):
            return f"""Hi {sender_name},

Thanks for reaching out! I'd be happy to connect you with our team.

For general inquiries, you can reach our support team at: support@company.com
For urgent matters, please call: +1 (555) 123-4567

I'm also forwarding your message to our support team who can provide more specific contact information based on your needs.

Best regards,
John"""

    elif any(word in body_lower for word in ['help', 'assistance', 'support']):
        return f"""Hello {sender_name},

Thank you for contacting us! I've received your message and I'm here to help.

I'm forwarding your request to our support team who will get back to you within 24 hours. In the meantime, you might find answers to common questions in our FAQ: https://company.com/faq

If this is urgent, please don't hesitate to call us at +1 (555) 123-4567.

Best regards,
John"""

    elif any(word in body_lower for word in ['meeting', 'schedule', 'appointment', 'call']):
        return f"""Hi {sender_name},

Thanks for your message! I'd be happy to schedule some time to chat.

Please let me know your availability and preferred time zone, and I'll coordinate with my calendar to find a suitable time.

I'm also copying our scheduling team on this email to help coordinate.

Looking forward to connecting!

Best regards,
John"""

    elif any(word in body_lower for word in ['price', 'cost', 'quote', 'pricing']):
        return f"""Hello {sender_name},

Thank you for your interest in our services! I'd be happy to provide you with pricing information.

I'm forwarding your inquiry to our sales team who will send you a detailed quote and answer any questions you might have about our packages.

You can also explore our pricing page here: https://company.com/pricing

Thanks for considering us!

Best regards,
John"""

    elif any(word in body_lower for word in ['job', 'career', 'position', 'hiring', 'resume']):
        return f"""Hi {sender_name},

Thank you for your interest in joining our team! It's always exciting to hear from potential new team members.

I'm forwarding your message to our HR department who will review your information and get back to you about current opportunities.

You can also check our careers page for open positions: https://company.com/careers

Best of luck!

Best regards,
John"""


    else:
        # Generic but friendly response
        return f"""Hi {sender_name},

Thanks for reaching out! I've received your message and I'm here to help.

I'm forwarding your email to the appropriate team member who can best assist you with your request. They'll get back to you within 24 hours.

If you have any questions in the meantime, feel free to reach out!

Best regards,
John"""

def process_new_emails(service, processed_ids):
    """Process new unread emails."""
    user_id = 'me'
    
    try:
        # Get unread emails
        results = service.users().messages().list(userId=user_id, labelIds=['INBOX', 'UNREAD']).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return processed_ids
        
        print(f"📧 Found {len(messages)} unread messages")
        
        for message_stub in messages:
            msg_id = message_stub['id']
            
            # Skip if already processed
            if msg_id in processed_ids:
                continue
                
            full_message = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
            # Extract email details
            headers = full_message['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
            body = get_message_body(full_message)
            
            print(f"\n🔄 Processing NEW email (ID: {msg_id}) from {sender}")
            print(f"   Subject: '{subject[:50]}...'")
            print(f"   Body: '{body[:100]}...'")
            
            # Rule-based classification with reply detection
            subject_lower = subject.lower()
            body_lower = body.lower()
            
            # Check if this is a direct question/request that needs a reply
            question_keywords = ['can you', 'please', 'send me', 'email', 'address', 'contact', 'manager', 'help', '?']
            is_question = any(word in body_lower for word in question_keywords) or '?' in body
            
            if is_question:
                classification = 'support'
                action = 'reply'
                reply_needed = True
                reply_text = generate_smart_reply(sender, subject, body)
                urgency = 'medium'
                reasoning = "Rule-based: Direct question detected, sending smart reply"
            elif any(word in subject_lower + body_lower for word in ['sales', 'buy', 'purchase', 'price', 'cost', 'quote', 'order']):
                classification = 'sales'
                action = 'forward'
                reply_needed = False
                reply_text = ""
                urgency = 'medium'
                reasoning = "Rule-based: Contains sales-related keywords"
            elif any(word in subject_lower + body_lower for word in ['support', 'help', 'issue', 'problem', 'bug', 'error', 'fix']):
                classification = 'support'
                action = 'forward'
                reply_needed = False
                reply_text = ""
                urgency = 'medium'
                reasoning = "Rule-based: Contains support-related keywords"
            elif any(word in subject_lower + body_lower for word in ['technical', 'api', 'integration', 'code', 'development']):
                classification = 'technical'
                action = 'forward'
                reply_needed = False
                reply_text = ""
                urgency = 'medium'
                reasoning = "Rule-based: Contains technical-related keywords"
            else:
                classification = 'support'
                action = 'forward'
                reply_needed = False
                reply_text = ""
                urgency = 'low'
                reasoning = "Rule-based: Default classification to support"
            
            print(f"  -> Analysis: {classification} | Action: {action} | Urgency: {urgency}")
            print(f"  -> Reasoning: {reasoning}")
            
            # Process the email
            if classification in CONTACTS:
                recipient = CONTACTS[classification]
                
                # Send reply if needed
                if action == "reply" and reply_needed:
                    print(f"  -> Sending reply to {sender}")
                    
                    reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
                    
                    # Extract Message-ID for threading
                    message_id = None
                    for header in full_message['payload'].get('headers', []):
                        if header['name'] == 'Message-ID':
                            message_id = header['value']
                            break
                    
                    reply_message = create_message(
                        sender=user_id, 
                        to=sender, 
                        subject=reply_subject, 
                        message_text=reply_text,
                        in_reply_to=message_id,
                        references=message_id
                    )
                    send_message(service, user_id, reply_message)
                
                # Forward to stakeholder
                if action == "forward" or action == "reply":
                    print(f"  -> Forwarding to {recipient}")
                    
                    urgency_prefix = f"[{urgency.upper()}] " if urgency != "low" else ""
                    forward_subject = f"FW: {urgency_prefix}[Auto-Routed] {subject}"
                    forward_body = f"""--- AUTOMATICALLY FORWARDED TO {classification.upper()} ---
Urgency: {urgency.upper()}
AI Analysis: {reasoning}
Reply Sent: {'Yes' if reply_needed else 'No'}

Original Email Details:
- From: {sender}
- Subject: {subject}

Original Message:
{body}

---
This email was automatically classified and forwarded by the AI Email Assistant.
{'An automated reply was sent to the original sender.' if reply_needed else ''}"""
                    
                    forward_message = create_message(sender=user_id, to=recipient, subject=forward_subject, message_text=forward_body)
                    send_message(service, user_id, forward_message)
                
                # Mark original message as READ
                service.users().messages().modify(
                    userId=user_id, 
                    id=msg_id, 
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                print("  -> Original email marked as read.")
                
                # Add to processed list
                processed_ids.add(msg_id)
                
            else:
                print(f"  -> Classification failed: {classification}. Skipping this email.")
        
        return processed_ids
        
    except Exception as e:
        print(f"❌ Error processing emails: {e}")
        return processed_ids

def main():
    """Main monitoring loop."""
    print("🤖 Starting Email Monitor...")
    print("   - Monitoring for new emails every 30 seconds")
    print("   - Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        service = get_gmail_service()
        print("✅ Connected to Gmail")
        
        # Initialize Bedrock client
        try:
            ai_client = boto3.client(
                service_name='bedrock-runtime', 
                region_name=AWS_REGION
            )
            print("✅ Connected to AWS Bedrock")
        except Exception as e:
            print(f"⚠️  Bedrock connection failed: {e}")
            print("   Using rule-based fallback only")
        
        processed_ids = set()
        
        while True:
            try:
                processed_ids = process_new_emails(service, processed_ids)
                print(f"⏰ Waiting 30 seconds... (Processed: {len(processed_ids)} emails)")
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping Email Monitor...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(30)
                
    except Exception as e:
        print(f"❌ Failed to start Email Monitor: {e}")

if __name__ == '__main__':
    main()
