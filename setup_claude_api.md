# Claude Sonnet 4 API Setup Guide

## Current Status
The AI assistant is working with intelligent intent analysis and tool access, but needs a valid Claude API key for advanced AI responses.

## Getting a Claude API Key

### Step 1: Sign up for Anthropic
1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Create an account or sign in
3. Verify your email address

### Step 2: Get API Access
1. Navigate to the API section
2. Request access to Claude Sonnet 4
3. Wait for approval (usually within 24-48 hours)

### Step 3: Generate API Key
1. Once approved, go to API Keys section
2. Click "Create Key"
3. Copy the generated key (starts with `sk-ant-`)

### Step 4: Set Environment Variable
```bash
export ANTHROPIC_API_KEY="your-claude-api-key-here"
```

Or add to your shell profile:
```bash
echo 'export ANTHROPIC_API_KEY="your-claude-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Current Features Working

✅ **Intent Analysis**: Intelligently categorizes emails
✅ **Tool Access**: Accesses company knowledge base
✅ **Disclosure Control**: Manages information sharing levels
✅ **Smart Forwarding**: Routes emails to appropriate contacts
✅ **Fallback System**: Works without Claude API

## Enhanced Features (with Claude API)

🚀 **Advanced AI Responses**: Contextual, human-like replies
🚀 **Conversation Flow**: Maintains context across emails
🚀 **Dynamic Information**: Adapts responses based on inquiry
🚀 **Professional Tone**: Matches company communication style

## Test the System

```bash
cd /Users/ritaachour/dev/email-assistant
python test_ai_assistant.py
```

## Usage

### Manual Processing
```bash
python email_assistant.py
```

### Continuous Monitoring
```bash
python email_monitor.py
```

## Knowledge Base Structure

The system includes:
- **Company Information**: Public and restricted details
- **Contact Directory**: Executive, management, and support contacts
- **Service Catalog**: Available services with pricing
- **Disclosure Policies**: Information sharing rules

## Example AI Response (with Claude)

**Input**: "can you send me the email address of your manager"

**AI Response**:
```
Hi Rita,

Thanks for reaching out! I'd be happy to connect you with our team.

For general inquiries, you can reach our support team at: support@techcorp.com
For urgent matters, please call: +1 (555) 123-4567

I'm also forwarding your message to our support team who can provide more specific contact information based on your needs.

Best regards,
John
```

The system automatically:
1. Analyzes the intent (executive contact request)
2. Determines disclosure level (standard)
3. Generates contextual response
4. Forwards to appropriate contact
5. Maintains professional tone
