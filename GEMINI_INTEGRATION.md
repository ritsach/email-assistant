# Gemini Integration Guide

## Overview
Since Gemini doesn't support MCP (Model Context Protocol), here are alternative ways to integrate your email assistant with Gemini.

## Option 1: Direct Integration (Recommended)

### Setup
1. Install dependencies:
```bash
cd /Users/ritaachour/dev/email-assistant
source venv/bin/activate
pip install flask
```

2. Run the integration script:
```bash
./run_gemini_integration.sh
```

### Usage
The integration script provides a conversational interface where you can ask Gemini about email management:

```
💬 Ask me about email management: Process my unread emails
🤖 Gemini Response: I'll help you process your unread emails...
📧 Processing emails...
Result: Emails processed successfully
```

## Option 2: Web API Integration

### Setup
1. Start the web API server:
```bash
./run_web_api.sh
```

2. The API will be available at: `http://localhost:5000`

### Available Endpoints

#### Process Emails
```bash
curl -X POST http://localhost:5000/api/process-emails
```

#### Analyze Email
```bash
curl -X POST http://localhost:5000/api/analyze-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "user@example.com",
    "subject": "Test Email",
    "body": "This is a test email"
  }'
```

#### Generate Reply
```bash
curl -X POST http://localhost:5000/api/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "user@example.com",
    "subject": "Test Email",
    "body": "This is a test email"
  }'
```

#### Health Check
```bash
curl http://localhost:5000/api/health
```

#### Get Capabilities
```bash
curl http://localhost:5000/api/capabilities
```

## Option 3: Gemini Code Assist Integration

### VS Code Integration
1. Install Gemini Code Assist extension in VS Code
2. Configure the extension to use your email assistant API
3. Use natural language to interact with your email system

### Configuration
Add to your VS Code settings:
```json
{
  "gemini.apiKey": "your-gemini-api-key",
  "gemini.emailAssistantUrl": "http://localhost:5000"
}
```

## Option 4: Custom Gemini Function Calling

### Implementation
Create a custom function calling system that Gemini can use:

```python
import google.generativeai as genai

def email_assistant_function(action, **kwargs):
    """Function that Gemini can call"""
    if action == "process_emails":
        return process_emails()
    elif action == "analyze_email":
        return analyze_email(kwargs.get('sender'), kwargs.get('subject'), kwargs.get('body'))
    elif action == "generate_reply":
        return generate_reply(kwargs.get('sender'), kwargs.get('subject'), kwargs.get('body'))
    else:
        return {"error": "Unknown action"}

# Configure Gemini with function calling
model = genai.GenerativeModel('gemini-1.5-pro')
```

## Usage Examples

### Process Emails
```
User: "Can you process my unread emails?"
Gemini: "I'll process your unread emails now..."
[Email assistant processes emails]
Gemini: "I've processed 3 unread emails. 2 were forwarded to support, 1 received a reply."
```

### Analyze Email
```
User: "Analyze this email: From: client@company.com, Subject: Urgent Issue, Body: We have a critical problem..."
Gemini: "I've analyzed the email. It's classified as 'support' with 'high' urgency. I recommend forwarding it to the technical team immediately."
```

### Generate Reply
```
User: "Generate a reply for: From: customer@example.com, Subject: Thank you, Body: Thanks for your help..."
Gemini: "Here's a professional reply: 'Hi Customer, You're very welcome! I'm glad I could help...'"
```

## Troubleshooting

### Common Issues
1. **API Key Not Set**: Ensure `GEMINI_API_KEY` is set in your environment
2. **Virtual Environment**: Always activate the virtual environment before running
3. **Port Conflicts**: If port 5000 is busy, change it in `web_api.py`

### Debug Mode
Run with debug output:
```bash
export FLASK_DEBUG=1
python web_api.py
```

## Security Considerations

1. **API Key Protection**: Never expose your Gemini API key in code
2. **Network Security**: Only expose the API on localhost for development
3. **Input Validation**: Validate all inputs to prevent injection attacks
4. **Rate Limiting**: Implement rate limiting for production use

## Next Steps

1. Choose your preferred integration method
2. Set up the necessary dependencies
3. Test the integration with sample emails
4. Customize the prompts and responses for your needs
5. Deploy to production if needed

## Support

For issues or questions:
- Check the logs in the terminal
- Verify API key configuration
- Ensure all dependencies are installed
- Test with simple examples first
