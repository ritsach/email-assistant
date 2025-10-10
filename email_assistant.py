"""
AI Email Assistant - Intelligent Email Processing System

This assistant automatically:
1. Analyzes incoming emails using AWS Bedrock (Claude 3)
2. Determines appropriate action: reply, forward, or both
3. Generates intelligent replies when needed
4. Forwards emails to key stakeholders (sales, support, technical)
5. Maintains proper email threading for replies
6. Marks processed emails as read

Features:
- Smart classification (sales/support/technical)
- Urgency detection (low/medium/high)
- Contextual reply generation
- Proper email forwarding with analysis
- Email threading support
"""

import os
import json # Nécessaire pour formater les requêtes Bedrock
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import anthropic # Using Anthropic SDK as fallback
import boto3 # <--- NOUVEAU : Le SDK AWS (Boto3)
import base64
from email.mime.text import MIMEText

# Import the new AI assistant system
from ai_assistant import ai_assistant

# Set Bedrock API key in environment variable
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "ABSKQmVkcm9ja0FQSUtleS03bXZoLWF0LTY2OTQ0NjEwMTEyNjpTZ2ZVK3FSMWJYR1BQcE54OENmY0RIWXhWRWJLelJJYUJnMVhFRXN1WGg0MmVFRWwzUWpBcjRqakxJZz0="
# --- CONFIGURATION (NOUVELLE CONFIGURATION POUR AWS) ---
CONTACTS = {
    "sales": "ads.al@laposte.net",
    "support": "victor.sana@berkeley.edu", 
    "technical": "idris.houiralami@berkeley.edu",
}

# AWS Bedrock Configuration
AWS_REGION = 'us-east-1'  # Change this to your preferred AWS region
BEDROCK_MODEL_ID = 'us.anthropic.claude-sonnet-4-20250514-v1:0'  # Claude Sonnet 4 model
# -----------------------------------------------------

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_gmail_service():
    """Handles authentication and returns the Gmail service object."""
    # ... (fonction inchangée) ...
    creds = None
    # Load credentials from token.json if it exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Run authentication flow if credentials are not valid or don't exist
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Starts the browser-based authentication flow
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_message_body(message):
    """Parses a Gmail message object to extract the plain text body."""
    # ... (fonction inchangée) ...
    msg_parts = message.get('payload', {}).get('parts', [])
    
    for part in msg_parts:
        # Check for plain text part
        if part['mimeType'] == 'text/plain':
            data = part['body'].get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')

    # Fallback for simple messages where the body is directly in the payload
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
    
    # Add threading headers if provided
    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
    if references:
        message['References'] = references
    
    # Encode message for Gmail API
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Sends the message via the Gmail API."""
    # ... (fonction inchangée) ...
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

def process_emails():
    """Main function to fetch, analyze, and process emails."""
    
    try:
        service = get_gmail_service()
    except Exception as e:
        print(f"ERROR: Failed to authenticate with Gmail. Check credentials.json and ensure it's a 'Desktop App'. Details: {e}")
        return

    # --- INITIALISATION DU CLIENT AWS BEDROCK ---
    try:
        # Boto3 trouve vos clés d'accès AWS (Access Key ID et Secret Access Key)
        # dans les variables d'environnement ou le fichier de configuration AWS.
        ai_client = boto3.client(
            service_name='bedrock-runtime', 
            region_name=AWS_REGION
        )
        print("Connected to Gmail and AWS Bedrock. Starting email processing...")
    except Exception as e:
        print(f"ERROR: Failed to initialize AWS Bedrock client. Ensure AWS_REGION is correct and AWS Credentials are set up locally. Details: {e}")
        return
    
    # --- MAIN LOGIC (The core of your assistant) ---
    user_id = 'me'
    
    try:
        # 1. Fetch unread emails
        results = service.users().messages().list(userId=user_id, labelIds=['INBOX', 'UNREAD']).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No unread messages found. Exiting.")
            return

        print(f"Found {len(messages)} unread messages to process.")

        for message_stub in messages:
            msg_id = message_stub['id']
            full_message = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
            # Extract email details
            headers = full_message['payload']['headers']
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            sender = next(header['value'] for header in headers if header['name'] == 'From')
            body = get_message_body(full_message)

            print(f"\nProcessing email (ID: {msg_id}) from {sender} with Subject: '{subject[:50]}...'")

            # 2. Analyse intelligente de l'e-mail avec IA
            analysis_prompt = f"""You are an intelligent email assistant. Analyze the following email and determine:

1. What type of inquiry this is (sales, support, technical)
2. Whether this requires an immediate reply, forwarding to stakeholders, or both
3. If a reply is needed, generate an appropriate response

EMAIL DETAILS:
- From: {sender}
- Subject: {subject}
- Body: {body}

Respond in JSON format:
{{
    "classification": "sales|support|technical",
    "action": "reply|forward|both",
    "reply_needed": true/false,
    "reply_text": "Your intelligent reply here (if reply_needed is true)",
    "urgency": "low|medium|high",
    "reasoning": "Brief explanation of your decision"
}}

Only respond with valid JSON, no additional text."""

            try:
                # Try Bedrock first
                response = ai_client.converse(
                    modelId=BEDROCK_MODEL_ID,
                    messages=[{"role": "user", "content": [{"text": analysis_prompt}]}]
                )
                
                # Parsing de la réponse Bedrock
                analysis_text = response["output"]["message"]["content"][0]["text"].strip()
                
            except Exception as e:
                print(f"  -> Bedrock failed: {e}, trying Anthropic SDK...")
                try:
                    # Fallback to Anthropic SDK
                    client = anthropic.Anthropic(api_key=os.environ["AWS_BEARER_TOKEN_BEDROCK"])
                    response = client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=500,
                        messages=[{"role": "user", "content": analysis_prompt}]
                    )
                    analysis_text = response.content[0].text.strip()
                except Exception as e2:
                    print(f"  -> Anthropic SDK also failed: {e2}")
                    print(f"  -> Using rule-based fallback classification...")
                    
                    # Rule-based fallback classification
                    subject_lower = subject.lower()
                    body_lower = body.lower()
                    
                    # Simple keyword-based classification with reply detection
                    if any(word in subject_lower + body_lower for word in ['sales', 'buy', 'purchase', 'price', 'cost', 'quote', 'order']):
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
                    elif any(word in subject_lower + body_lower for word in ['technical', 'api', 'integration', 'code', 'development', 'technical']):
                        classification = 'technical'
                        action = 'forward'
                        reply_needed = False
                        reply_text = ""
                        urgency = 'medium'
                        reasoning = "Rule-based: Contains technical-related keywords"
                    else:
                        # Check if this is a direct question/request that needs a reply
                        question_keywords = ['can you', 'please', 'send me', 'email', 'address', 'contact', 'manager', 'help', '?']
                        is_question = any(word in body_lower for word in question_keywords) or '?' in body
                        
                        if is_question:
                            # Use AI assistant for intelligent analysis and reply generation
                            intent_analysis = ai_assistant.analyze_email_intent(sender, subject, body)
                            
                            classification = intent_analysis["intent"]["category"]
                            action = 'reply' if ai_assistant.should_reply(intent_analysis) else 'forward'
                            reply_needed = ai_assistant.should_reply(intent_analysis)
                            
                            if reply_needed:
                                reply_text = ai_assistant.generate_intelligent_reply(sender, subject, body)
                            else:
                                reply_text = ""
                            
                            urgency = intent_analysis["intent"]["urgency"]
                            reasoning = f"AI Analysis: {intent_analysis['intent']['primary_intent']} detected"
                        else:
                            classification = 'support'  # Default to support
                            action = 'forward'
                            reply_needed = False
                            reply_text = ""
                            urgency = 'low'
                            reasoning = "Rule-based: Default classification to support"
                    
                    print(f"  -> Fallback Analysis: {classification} | Action: {action} | Urgency: {urgency}")
                    print(f"  -> Reasoning: {reasoning}")
            
            # Parse JSON response (only if we have analysis_text from AI)
            if 'analysis_text' in locals():
                try:
                    analysis = json.loads(analysis_text)
                    classification = analysis.get('classification', '').lower()
                    action = analysis.get('action', '').lower()
                    reply_needed = analysis.get('reply_needed', False)
                    reply_text = analysis.get('reply_text', '')
                    urgency = analysis.get('urgency', 'low')
                    reasoning = analysis.get('reasoning', '')
                    
                    print(f"  -> AI Analysis: {classification} | Action: {action} | Urgency: {urgency}")
                    print(f"  -> Reasoning: {reasoning}")
                    
                except json.JSONDecodeError as e:
                    print(f"  -> Failed to parse AI response as JSON: {e}")
                    print(f"  -> Raw response: {analysis_text}")
                    classification = None
                    action = None
                    reply_needed = False
                    reply_text = ""
                    urgency = "low"
                    reasoning = "JSON parsing failed"
            
            # 3. Traitement intelligent basé sur l'analyse IA
            print(f"  -> DEBUG: classification='{classification}', CONTACTS={list(CONTACTS.keys())}")
            
            # Determine recipient using AI assistant if available
            if 'intent_analysis' in locals():
                ai_recipient = ai_assistant.get_forwarding_recipient(intent_analysis)
                if ai_recipient:
                    recipient = ai_recipient
                    print(f"  -> AI selected recipient: {recipient}")
                elif classification in CONTACTS:
                    recipient = CONTACTS[classification]
                else:
                    recipient = None
            elif classification in CONTACTS:
                recipient = CONTACTS[classification]
            else:
                recipient = None
            
            if recipient:
                
                # Action: Reply only
                if action == "reply" and reply_needed:
                    print(f"  -> Classified as '{classification}'. Sending intelligent reply to {sender}")
                    
                    # Create reply with proper threading
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
                    
                # Action: Forward only
                elif action == "forward":
                    print(f"  -> Classified as '{classification}'. Forwarding to {recipient}")
                    
                    urgency_prefix = f"[{urgency.upper()}] " if urgency != "low" else ""
                    forward_subject = f"FW: {urgency_prefix}[Auto-Routed] {subject}"
                    forward_body = f"""--- AUTOMATICALLY FORWARDED TO {classification.upper()} ---
Urgency: {urgency.upper()}
AI Analysis: {reasoning}

Original Email Details:
- From: {sender}
- Subject: {subject}
- Date: {full_message.get('internalDate', 'Unknown')}

Original Message:
{body}

---
This email was automatically classified and forwarded by the AI Email Assistant."""
                    
                    forward_message = create_message(sender=user_id, to=recipient, subject=forward_subject, message_text=forward_body)
                    send_message(service, user_id, forward_message)
                    
                # Action: Both reply and forward
                elif action == "both":
                    print(f"  -> Classified as '{classification}'. Sending reply to {sender} AND forwarding to {recipient}")
                    
                    # Send reply first
                    if reply_needed:
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
                    
                    # Then forward to stakeholder
                    urgency_prefix = f"[{urgency.upper()}] " if urgency != "low" else ""
                    forward_subject = f"FW: {urgency_prefix}[Auto-Routed] {subject}"
                    forward_body = f"""--- AUTOMATICALLY FORWARDED TO {classification.upper()} ---
Urgency: {urgency.upper()}
AI Analysis: {reasoning}
Reply Sent: {'Yes' if reply_needed else 'No'}

Original Email Details:
- From: {sender}
- Subject: {subject}
- Date: {full_message.get('internalDate', 'Unknown')}

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

            else:
                print(f"  -> Classification failed or was not recognized: {classification}. Skipping this email.")

    except Exception as e:
        print(f"An error occurred during email processing: {e}")


if __name__ == '__main__':
    process_emails()