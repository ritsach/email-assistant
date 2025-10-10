#!/usr/bin/env python3
"""
Script to check the latest email received and verify if it was processed
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from datetime import datetime

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_gmail_service():
    """Handles authentication and returns the Gmail service object."""
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

def check_latest_email():
    """Check the latest email and its processing status."""
    try:
        service = get_gmail_service()
        user_id = 'me'
        
        print("🔍 Checking latest emails...")
        
        # Get the latest 5 messages
        results = service.users().messages().list(
            userId=user_id, 
            labelIds=['INBOX'], 
            maxResults=5
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("❌ No messages found in inbox")
            return
        
        print(f"📧 Found {len(messages)} recent messages")
        print("=" * 80)
        
        for i, message_stub in enumerate(messages):
            msg_id = message_stub['id']
            full_message = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
            # Extract email details
            headers = full_message['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
            date = next((header['value'] for header in headers if header['name'] == 'Date'), 'Unknown Date')
            
            # Check if message is read or unread
            labels = full_message.get('labelIds', [])
            is_read = 'UNREAD' not in labels
            
            # Get message body preview
            body = get_message_body(full_message)
            body_preview = body[:100] + "..." if len(body) > 100 else body
            
            print(f"📨 Email #{i+1} (ID: {msg_id})")
            print(f"   From: {sender}")
            print(f"   Subject: {subject}")
            print(f"   Date: {date}")
            print(f"   Status: {'✅ READ' if is_read else '🔴 UNREAD'}")
            print(f"   Body Preview: {body_preview}")
            print("-" * 80)
            
            # Check if this is the latest email
            if i == 0:
                print(f"🎯 LATEST EMAIL ANALYSIS:")
                print(f"   Message ID: {msg_id}")
                print(f"   From: {sender}")
                print(f"   Subject: {subject}")
                print(f"   Processed: {'✅ YES' if is_read else '❌ NO (still unread)'}")
                
                if is_read:
                    print(f"   ✅ This email has been processed by the assistant")
                else:
                    print(f"   ❌ This email has NOT been processed yet")
                    print(f"   💡 Run the email assistant to process it")
                print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")

if __name__ == '__main__':
    check_latest_email()
