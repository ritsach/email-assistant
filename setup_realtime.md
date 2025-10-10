# Real-time Email Processing Setup Guide

## Current Status
Your email assistant currently runs manually. To make it process emails automatically when they arrive, you have several options:

## Option 1: Email Monitor Script (Recommended)
Run the `email_monitor.py` script to continuously monitor for new emails:

```bash
cd /Users/ritaachour/dev/email-assistant
python email_monitor.py
```

This script:
- Checks for new emails every 30 seconds
- Automatically processes and replies to them
- Runs continuously until you stop it (Ctrl+C)

## Option 2: Google Cloud Pub/Sub (Advanced)
For true real-time processing, you can set up Google Cloud Pub/Sub:

### Step 1: Enable Gmail Push Notifications
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0)

### Step 2: Set up Pub/Sub
1. Enable Cloud Pub/Sub API
2. Create a topic: `gmail-notifications`
3. Create a subscription: `email-processor`

### Step 3: Configure Gmail Watch
```python
# Add this to your email assistant
def setup_gmail_watch(service):
    """Set up Gmail push notifications"""
    request = {
        'labelIds': ['INBOX'],
        'topicName': 'projects/YOUR_PROJECT_ID/topics/gmail-notifications'
    }
    
    response = service.users().watch(userId='me', body=request).execute()
    print(f"Gmail watch set up: {response}")
    return response['expiration']
```

### Step 4: Create Cloud Function
Create a Google Cloud Function that triggers on Pub/Sub messages:

```python
# main.py for Cloud Function
import base64
import json
from email_assistant import process_emails

def process_email_notification(event, context):
    """Cloud Function triggered by Gmail notifications"""
    if 'data' in event:
        message = base64.b64decode(event['data']).decode('utf-8')
        data = json.loads(message)
        
        if data.get('emailAddress') == 'johnweakagent@gmail.com':
            process_emails()
    
    return 'OK'
```

## Option 3: Cron Job (Simple)
Set up a cron job to run the assistant every few minutes:

```bash
# Edit crontab
crontab -e

# Add this line to run every 5 minutes
*/5 * * * * cd /Users/ritaachour/dev/email-assistant && python email_assistant.py
```

## Option 4: Systemd Service (Linux/Mac)
Create a systemd service for automatic startup:

```ini
# /etc/systemd/system/email-assistant.service
[Unit]
Description=Email Assistant
After=network.target

[Service]
Type=simple
User=ritaachour
WorkingDirectory=/Users/ritaachour/dev/email-assistant
ExecStart=/usr/bin/python3 email_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable it:
```bash
sudo systemctl enable email-assistant
sudo systemctl start email-assistant
```

## Recommendation
For immediate use, **Option 1 (Email Monitor)** is the easiest:
- No Google Cloud setup required
- Works immediately
- Handles replies and forwarding
- Easy to stop/start

Run: `python email_monitor.py` and it will continuously monitor for new emails!
