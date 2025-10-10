# MCP Server Setup Guide

## Overview

Your email assistant has been converted to an MCP (Model Context Protocol) server while preserving all original functionality. This allows AI clients like Claude Desktop to interact with your email assistant through standardized tools.

## Architecture

### Dual Mode Operation

1. **Standalone Mode**: Original functionality preserved
   ```bash
   python standalone_assistant.py
   ```

2. **MCP Server Mode**: Exposes tools for AI clients
   ```bash
   python mcp_server.py
   ```

### Preserved Core Functions

✅ **Email Processing**: Analyze, reply, and forward emails  
✅ **Intent Analysis**: Smart classification and urgency detection  
✅ **AI Responses**: Claude Sonnet 4 powered replies  
✅ **Knowledge Base**: Company info and contact management  
✅ **Disclosure Control**: Information sharing policies  
✅ **Email Threading**: Proper conversation context  

## MCP Tools Available

### Email Processing Tools
- `process_unread_emails()` - Process all unread emails
- `analyze_email_intent()` - Analyze email intent and action
- `generate_email_reply()` - Generate intelligent replies

### Email Management Tools
- `get_unread_emails()` - List unread emails
- `get_email_content()` - Get full email content

### Knowledge Base Tools
- `get_company_info()` - Get company information
- `search_contacts()` - Search contact directory
- `get_contact_info()` - Get specific contact info

### Configuration Tools
- `get_contacts_config()` - Get current contacts
- `update_contacts_config()` - Update contacts

## Setup Instructions

### 1. Install MCP Dependencies

```bash
cd /Users/ritaachour/dev/email-assistant
pip install -r requirements.txt
```

### 2. Test Standalone Mode

```bash
python standalone_assistant.py
```

### 3. Test MCP Server Mode

```bash
python mcp_server.py
```

### 4. Connect to Claude Desktop

1. **Locate Claude Desktop config**:
   ```bash
   # macOS
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **Add MCP server configuration**:
   ```json
   {
     "mcpServers": {
       "email-assistant": {
         "command": "python",
         "args": ["/Users/ritaachour/dev/email-assistant/mcp_server.py"],
         "env": {
           "PYTHONPATH": "/Users/ritaachour/dev/email-assistant"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### 5. Verify Connection

In Claude Desktop, you should see the email assistant tools available. Try asking:
- "Process my unread emails"
- "Analyze this email intent: [email details]"
- "Get my company information"

## Usage Examples

### Via Claude Desktop

**Process Emails**:
```
Please process my unread emails and let me know what actions were taken.
```

**Analyze Email**:
```
Analyze the intent of this email:
From: customer@example.com
Subject: Pricing Inquiry
Body: What are your pricing options for the premium package?
```

**Get Contact Info**:
```
Get contact information for the sales department.
```

### Via Standalone Script

```bash
# Process emails automatically
python standalone_assistant.py

# Monitor continuously
python email_monitor.py
```

## Benefits of MCP Integration

### 1. **AI Client Integration**
- Claude Desktop can directly control your email assistant
- Natural language interface for email management
- Contextual assistance with email processing

### 2. **Preserved Functionality**
- All original features remain intact
- Same intelligent processing and analysis
- Same knowledge base and disclosure controls

### 3. **Enhanced Capabilities**
- AI can reason about email processing decisions
- Contextual help and explanations
- Integration with other AI tools and workflows

### 4. **Flexibility**
- Use standalone mode for automation
- Use MCP mode for AI-assisted management
- Switch between modes as needed

## Troubleshooting

### Common Issues

1. **MCP Server Not Starting**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"
   
   # Test imports
   python -c "from email_assistant import get_gmail_service"
   ```

2. **Claude Desktop Not Connecting**
   - Verify config file path
   - Check Python executable path
   - Ensure all dependencies installed

3. **Gmail API Issues**
   - Verify credentials.json exists
   - Check OAuth token validity
   - Ensure Gmail API is enabled

### Debug Mode

Enable debug output by modifying the MCP server:

```python
# Add to mcp_server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- **Credentials**: Same security as original assistant
- **API Keys**: Protected in environment variables
- **Access Control**: MCP tools respect disclosure levels
- **Audit Trail**: All actions logged and traceable

## Next Steps

1. **Test both modes** to ensure functionality
2. **Configure Claude Desktop** for MCP integration
3. **Explore AI-assisted email management**
4. **Customize tools** for your specific needs
5. **Monitor performance** and optimize as needed

## Support

- **Documentation**: See README.md for original setup
- **Issues**: Create GitHub issues for problems
- **MCP Protocol**: See [Model Context Protocol docs](https://modelcontextprotocol.io/)

---

**Note**: This MCP implementation preserves all original functionality while adding AI client integration capabilities. You can use either mode depending on your needs.
