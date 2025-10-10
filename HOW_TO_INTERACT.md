# How to Interact with Your Email Assistant MCP Server

## 🎯 Quick Start

Your email assistant is now configured as an MCP server! Here's how to interact with it:

## 📱 Method 1: Claude Desktop (Recommended)

### Step 1: Restart Claude Desktop
1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. The email assistant should now be available as an MCP tool

### Step 2: Verify Connection
In Claude Desktop, you should see the email assistant tools available. Try asking:

```
"List all available tools"
```

You should see tools like:
- `process_unread_emails`
- `analyze_email_intent`
- `generate_email_reply`
- `get_unread_emails`
- `get_company_info`
- `search_contacts`

### Step 3: Start Using Email Tools

**Process Emails:**
```
"Please process my unread emails and tell me what actions were taken."
```

**Analyze Email Intent:**
```
"Analyze the intent of this email:
From: customer@example.com
Subject: Pricing Inquiry
Body: What are your pricing options for the premium package?"
```

**Get Company Information:**
```
"Get our company information for a sales inquiry."
```

**Search Contacts:**
```
"Search for contacts related to 'manager' or 'executive'."
```

**Generate Reply:**
```
"Generate a reply for this email:
From: Rita Achour <rita@example.com>
Subject: Contact Information
Body: can you send me the email address of your manager"
```

## 🖥️ Method 2: Direct MCP Client

### Using MCP Inspector
```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Connect to your server
mcp-inspector python /Users/ritaachour/dev/email-assistant/mcp_server.py
```

### Using Python MCP Client
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(StdioServerParameters(
        command="python",
        args=["/Users/ritaachour/dev/email-assistant/mcp_server.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)
            
            # Call a tool
            result = await session.call_tool(
                "analyze_email_intent",
                {
                    "sender": "test@example.com",
                    "subject": "Test",
                    "body": "This is a test email"
                }
            )
            print("Result:", result)

asyncio.run(main())
```

## 🔧 Method 3: Standalone Mode (Original Functionality)

If you want to use the original functionality without MCP:

```bash
cd /Users/ritaachour/dev/email-assistant
python standalone_assistant.py
```

## 📋 Available MCP Tools

### Email Processing
- **`process_unread_emails()`** - Process all unread emails
- **`analyze_email_intent(sender, subject, body)`** - Analyze email intent
- **`generate_email_reply(sender, subject, body)`** - Generate intelligent reply

### Email Management
- **`get_unread_emails(limit=10)`** - Get list of unread emails
- **`get_email_content(message_id)`** - Get full email content

### Knowledge Base
- **`get_company_info(inquiry_context)`** - Get company information
- **`search_contacts(query)`** - Search contact directory
- **`get_contact_info(contact_type, inquiry_context)`** - Get specific contact info

### Employee Information Tools
- **`get_employee_info(email, disclosure_level)`** - Get employee information with disclosure control
- **`get_employee_summary(email)`** - Get employee summary for forwarding decisions
- **`search_employees_by_skill(skill)`** - Search employees by skill
- **`search_employees_by_role(role)`** - Search employees by role
- **`get_best_employee_for_inquiry(inquiry_type)`** - Get best employee for specific inquiry type
- **`should_forward_to_employee(email, inquiry_type)`** - Check if inquiry should be forwarded to employee
- **`get_all_employees(disclosure_level)`** - Get all employees with filtered information

### Configuration
- **`get_contacts_config()`** - Get current contacts
- **`update_contacts_config(contacts)`** - Update contacts

## 🎯 Example Conversations

### Process Emails
```
You: "Process my unread emails"
Claude: I'll process your unread emails now.
[Uses process_unread_emails tool]
Claude: I've processed 3 unread emails:
1. Sales inquiry from customer@example.com - forwarded to sales team
2. Support request from user@company.com - replied with assistance
3. Thank you message from client@business.com - acknowledged
```

### Analyze Email
```
You: "Analyze this email: From: manager@company.com, Subject: Urgent Request, Body: We need immediate assistance with our system"
Claude: I'll analyze this email for you.
[Uses analyze_email_intent tool]
Claude: This email has been classified as:
- Intent: Urgent request
- Category: Support
- Urgency: High
- Action: Both reply and forward
- Recommended recipient: Support team
```

### Get Contact Information
```
You: "Get contact information for the sales department"
Claude: I'll get the sales contact information for you.
[Uses get_contact_info tool]
Claude: Here's the sales contact information:
- Name: David Rodriguez
- Email: david.rodriguez@techcorp.com
- Phone: +1 (555) 200-0001
- Title: VP of Sales
```

**Get Employee Information:**
```
You: "Get information about Alexandre Dubois"
Claude: I'll get Alexandre's information for you.
[Uses get_employee_info tool]
Claude: Here's Alexandre's information:
- Name: Alexandre Dubois
- Role: Sales Director
- Department: Sales
- Skills: Sales Strategy, CRM Management, Client Relationship Management
- Office: Paris Headquarters, Floor 3, Office 301
```

**Search Employees by Skill:**
```
You: "Find employees with technical skills"
Claude: I'll search for employees with technical skills.
[Uses search_employees_by_skill tool]
Claude: Found employees with technical skills:
- Idris Houiralami (Technical Lead) - Software Architecture, Cloud Computing, DevOps
- Victor Sana (Support Manager) - Technical Troubleshooting, Incident Management
```

**Get Best Employee for Inquiry:**
```
You: "Who should handle a sales inquiry?"
Claude: I'll find the best employee for sales inquiries.
[Uses get_best_employee_for_inquiry tool]
Claude: For sales inquiries, the best person is:
- Alexandre Dubois (Sales Director)
- Email: ads.al@laposte.net
- Phone: +33 1 42 86 12 34
- Office: Paris Headquarters, Floor 3, Office 301
```

## 🚨 Troubleshooting

### Claude Desktop Not Showing Tools
1. **Check Configuration**: Verify `claude_desktop_config.json` is correct
2. **Restart Claude**: Completely quit and reopen Claude Desktop
3. **Check Python Path**: Ensure the Python path in config is correct
4. **Check Dependencies**: Make sure all packages are installed

### MCP Server Not Starting
1. **Check Python Environment**: Ensure you're using the correct virtual environment
2. **Check Dependencies**: Run `pip install -r requirements.txt`
3. **Check Gmail API**: Ensure `credentials.json` exists and is valid
4. **Check AWS Credentials**: Verify AWS credentials are set up

### Tools Not Working
1. **Check Gmail Connection**: Test with `python standalone_assistant.py`
2. **Check AWS Bedrock**: Verify API key and region
3. **Check Permissions**: Ensure Gmail API has modify permissions
4. **Check Logs**: Look for error messages in Claude Desktop

## 🔍 Debug Mode

To see what's happening behind the scenes:

1. **Check Claude Desktop Logs**: Look for MCP-related messages
2. **Test Standalone Mode**: Verify core functionality works
3. **Check MCP Server**: Test server directly
4. **Verify Configuration**: Double-check all paths and settings

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Claude Desktop shows email assistant tools
- ✅ You can ask Claude to process emails
- ✅ Claude can analyze email intent
- ✅ Claude can generate replies
- ✅ Claude can access company information

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Test standalone mode first
3. Verify all dependencies are installed
4. Check Claude Desktop configuration
5. Restart Claude Desktop

---

**Happy email managing!** Your AI assistant is now ready to help you process emails through Claude Desktop. 🚀
