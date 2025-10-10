#!/usr/bin/env python3
"""
MCP Server for AI Email Assistant
Exposes email processing capabilities as MCP tools while preserving core functionality
"""

import os
import sys
import json
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
from email_assistant import get_gmail_service, process_emails, CONTACTS
from ai_assistant import ai_assistant
from knowledge_base import knowledge_base, tool_system

# Initialize MCP server
mcp = FastMCP("email-assistant")

# Global service instance
gmail_service = None

def _ensure_gmail_service():
    """Ensure Gmail service is initialized."""
    global gmail_service
    if gmail_service is None:
        try:
            gmail_service = get_gmail_service()
        except Exception as e:
            raise Exception(f"Failed to initialize Gmail service: {e}")

def _format_response(data: Any) -> str:
    """Format response data as JSON."""
    return json.dumps(data, indent=2, sort_keys=True)

# ===== Email Processing Tools =====

@mcp.tool()
async def process_unread_emails() -> str:
    """
    Process all unread emails in the inbox.
    This is the main function that analyzes, replies, and forwards emails.
    """
    try:
        _ensure_gmail_service()
        
        # Use the existing process_emails function
        result = process_emails()
        
        return _format_response({
            "status": "success",
            "message": "Unread emails processed successfully",
            "result": result
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to process emails: {str(e)}"
        })

@mcp.tool()
async def analyze_email_intent(sender: str, subject: str, body: str) -> str:
    """
    Analyze email intent and determine appropriate action.
    
    Args:
        sender: Email sender
        subject: Email subject
        body: Email body content
    """
    try:
        intent_analysis = ai_assistant.analyze_email_intent(sender, subject, body)
        
        return _format_response({
            "status": "success",
            "intent_analysis": intent_analysis["intent"],
            "response_info": intent_analysis["response_info"],
            "should_reply": ai_assistant.should_reply(intent_analysis),
            "forwarding_recipient": ai_assistant.get_forwarding_recipient(intent_analysis)
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to analyze email intent: {str(e)}"
        })

@mcp.tool()
async def generate_email_reply(sender: str, subject: str, body: str) -> str:
    """
    Generate an intelligent reply for an email.
    
    Args:
        sender: Email sender
        subject: Email subject
        body: Email body content
    """
    try:
        reply = ai_assistant.generate_intelligent_reply(sender, subject, body)
        
        return _format_response({
            "status": "success",
            "reply": reply,
            "sender": sender,
            "subject": subject
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to generate reply: {str(e)}"
        })

# ===== Email Management Tools =====

@mcp.tool()
async def get_unread_emails(limit: int = 10) -> str:
    """
    Get list of unread emails from inbox.
    
    Args:
        limit: Maximum number of emails to retrieve (default: 10)
    """
    try:
        _ensure_gmail_service()
        
        results = gmail_service.users().messages().list(
            userId='me', 
            labelIds=['INBOX', 'UNREAD'],
            maxResults=limit
        ).execute()
        
        messages = results.get('messages', [])
        email_list = []
        
        for message_stub in messages:
            msg_id = message_stub['id']
            full_message = gmail_service.users().messages().get(userId='me', id=msg_id).execute()
            
            headers = full_message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            email_list.append({
                "id": msg_id,
                "subject": subject,
                "sender": sender,
                "date": date
            })
        
        return _format_response({
            "status": "success",
            "count": len(email_list),
            "emails": email_list
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to get unread emails: {str(e)}"
        })

@mcp.tool()
async def get_email_content(message_id: str) -> str:
    """
    Get full content of a specific email.
    
    Args:
        message_id: Gmail message ID
    """
    try:
        _ensure_gmail_service()
        
        full_message = gmail_service.users().messages().get(userId='me', id=message_id).execute()
        
        headers = full_message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        
        # Extract body (simplified)
        body = ""
        if 'parts' in full_message['payload']:
            for part in full_message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = part['body']['data']
                    break
        
        return _format_response({
            "status": "success",
            "message_id": message_id,
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to get email content: {str(e)}"
        })

# ===== Knowledge Base Tools =====

@mcp.tool()
async def get_company_info(inquiry_context: str = "") -> str:
    """
    Get company information with appropriate disclosure level.
    
    Args:
        inquiry_context: Context about the inquiry (optional)
    """
    try:
        context = json.loads(inquiry_context) if inquiry_context else {}
        company_info = knowledge_base.get_company_info(context)
        
        return _format_response({
            "status": "success",
            "company_info": company_info
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to get company info: {str(e)}"
        })

@mcp.tool()
async def search_contacts(query: str) -> str:
    """
    Search for contacts by name, title, or role.
    
    Args:
        query: Search term
    """
    try:
        results = knowledge_base.search_contacts(query)
        
        return _format_response({
            "status": "success",
            "query": query,
            "results": results
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to search contacts: {str(e)}"
        })

@mcp.tool()
async def get_contact_info(contact_type: str, inquiry_context: str = "") -> str:
    """
    Get contact information for specific roles or departments.
    
    Args:
        contact_type: Type of contact (executive, management, support)
        inquiry_context: Context about the inquiry (optional)
    """
    try:
        context = json.loads(inquiry_context) if inquiry_context else {}
        contact_info = knowledge_base.get_contact_info(contact_type, context)
        
        return _format_response({
            "status": "success",
            "contact_type": contact_type,
            "contact_info": contact_info
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to get contact info: {str(e)}"
        })

# ===== Configuration Tools =====

@mcp.tool()
async def get_contacts_config() -> str:
    """
    Get current contacts configuration.
    """
    try:
        return _format_response({
            "status": "success",
            "contacts": CONTACTS
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to get contacts config: {str(e)}"
        })

@mcp.tool()
async def update_contacts_config(contacts: str) -> str:
    """
    Update contacts configuration.
    
    Args:
        contacts: JSON string with new contacts configuration
    """
    try:
        new_contacts = json.loads(contacts)
        # Update global CONTACTS
        CONTACTS.update(new_contacts)
        
        return _format_response({
            "status": "success",
            "message": "Contacts configuration updated",
            "contacts": CONTACTS
        })
    except Exception as e:
        return _format_response({
            "status": "error",
            "message": f"Failed to update contacts config: {str(e)}"
        })

# ===== Server Management =====

def run_server() -> None:
    """Start the MCP server over stdio."""
    print("Starting Email Assistant MCP Server...", file=sys.stderr)
    
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Email Assistant MCP Server stopped", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    run_server()
