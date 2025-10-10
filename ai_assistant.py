#!/usr/bin/env python3
"""
Advanced AI Email Assistant with Claude Sonnet 4 and Tool Access
"""

import os
import json
import boto3
from typing import Dict, List, Any, Optional
from knowledge_base import knowledge_base, tool_system
from private_knowledge_base import private_kb

class AIEmailAssistant:
    """Advanced AI Email Assistant with Claude Sonnet 4 and tool access."""
    
    def __init__(self):
        # Set up Bedrock API key
        self.api_key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "ABSKQmVkcm9ja0FQSUtleS03bXZoLWF0LTY2OTQ0NjEwMTEyNjpTZ2ZVK3FSMWJYR1BQcE54OENmY0RIWXhWRWJLelJJYUJnMVhFRXN1WGg0MmVFRWwzUWpBcjRqakxJZz0=")
        
        # Initialize Bedrock client with explicit credentials
        self.client = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1",
            aws_access_key_id="BedrockAPIKey-7mvh-at-669446101126",
            aws_secret_access_key="SgfU+qR1bXGPPnX8CfcDHXxVEbKzRIaBg1XEsuXh42eEEl3QjAr4jjLIg="
        )
        
        # Assistant configuration
        self.assistant_name = "John"
        self.assistant_role = "Executive Assistant"
        self.company_name = "TechCorp Solutions"
        
    def generate_intelligent_reply(self, sender: str, subject: str, body: str, 
                                 sender_email: str = "") -> str:
        """Generate intelligent, contextual reply using Claude Sonnet 4."""
        
        # Get appropriate information for this inquiry
        inquiry_context = {
            "sender": sender_email or sender,
            "subject": subject,
            "body": body
        }
        
        response_info = tool_system.execute_tool("get_response_info", {
            "inquiry_context": inquiry_context
        })
        
        # Extract sender name
        sender_name = sender.split('<')[0].strip() if '<' in sender else sender.split('@')[0]
        
        # Create system prompt
        system_prompt = self._create_system_prompt(response_info)
        
        # Create user prompt
        user_prompt = self._create_user_prompt(sender_name, subject, body, response_info)
        
        try:
            # Call Claude Sonnet 4 via Bedrock
            response = self.client.converse(
                modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
                messages=[{"role": "user", "content": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}]
            )
            
            return response["output"]["message"]["content"][0]["text"].strip()
            
        except Exception as e:
            print(f"Claude API error: {e}")
            # Fallback to rule-based response
            return self._generate_fallback_reply(sender_name, subject, body, response_info)
    
    def _create_system_prompt(self, response_info: Dict[str, Any]) -> str:
        """Create system prompt for Claude with context and tools."""
        
        disclosure_level = response_info.get("disclosure_level", "standard")
        company_info = response_info.get("company_info", {})
        contacts = response_info.get("contacts", [])
        services = response_info.get("services", [])
        policies = response_info.get("policies", {})
        
        system_prompt = f"""You are {self.assistant_name}, an {self.assistant_role} at {company_info.get('name', self.company_name)}. 

Your role is to respond to emails in a professional, helpful, and human-like manner. You have access to company information and tools to provide accurate responses.

COMPANY INFORMATION:
- Name: {company_info.get('name', 'TechCorp Solutions')}
- Website: {company_info.get('website', 'https://techcorp.com')}
- Industry: {company_info.get('industry', 'Technology Solutions')}
- Mission: {company_info.get('mission', 'Empowering businesses with innovative technology solutions')}

DISCLOSURE LEVEL: {disclosure_level.upper()}
Based on the inquiry context, you are authorized to share information at the {disclosure_level} level.

AVAILABLE CONTACTS:
"""
        
        for contact in contacts:
            contact_info = contact["info"]
            system_prompt += f"- {contact_info['name']} ({contact_info['title']}): {contact_info['email']}\n"
        
        if services:
            system_prompt += "\nAVAILABLE SERVICES:\n"
            for service in services:
                system_prompt += f"- {service['name']}: {service['description']}\n"
                if disclosure_level == "high":
                    system_prompt += f"  Pricing: {service.get('pricing', 'Contact for pricing')}\n"
        
        system_prompt += f"""
POLICIES:
- Response Time: {policies.get('response_time', '24 hours')}
- Emergency Contact: {policies.get('emergency', 'Call +1 (555) 911-HELP')}
- Privacy: {policies.get('privacy', 'Strict confidentiality maintained')}

INSTRUCTIONS:
1. Respond in a warm, professional, and human-like tone
2. Use the sender's name naturally in your response
3. Provide relevant information based on the inquiry
4. Respect disclosure levels - only share information appropriate for the {disclosure_level} level
5. Include appropriate contact information when relevant
6. Forward to appropriate team members when necessary
7. Maintain conversation flow and context
8. Be helpful but not overly verbose
9. Sign your responses as "{self.assistant_name}"

RESPONSE FORMAT:
- Use proper email formatting
- Include appropriate greeting and closing
- Be conversational but professional
- Provide clear next steps when applicable
"""
        
        return system_prompt
    
    def _create_user_prompt(self, sender_name: str, subject: str, body: str, 
                           response_info: Dict[str, Any]) -> str:
        """Create user prompt with email context."""
        
        return f"""Please respond to this email:

FROM: {sender_name}
SUBJECT: {subject}
BODY: {body}

Context: This inquiry has been classified as {response_info.get('disclosure_level', 'standard')} disclosure level.

Please provide a helpful, professional response that:
1. Addresses their specific request
2. Provides relevant information based on their inquiry
3. Includes appropriate contact information if needed
4. Maintains a warm, human-like tone
5. Respects the disclosure level for this inquiry

Respond as if you are {self.assistant_name}, the {self.assistant_role} at {self.company_name}."""
    
    def _generate_fallback_reply(self, sender_name: str, subject: str, body: str, 
                                response_info: Dict[str, Any]) -> str:
        """Generate fallback reply when Claude is unavailable."""
        
        contacts = response_info.get("contacts", [])
        company_info = response_info.get("company_info", {})
        
        # Get primary contact
        primary_contact = contacts[0]["info"] if contacts else {
            "name": "Support Team",
            "email": "support@techcorp.com",
            "phone": "+1 (555) 123-4567"
        }
        
        return f"""Hi {sender_name},

Thank you for reaching out to {company_info.get('name', self.company_name)}! I've received your message and I'm here to help.

I'm forwarding your inquiry to our {primary_contact['name']} who will get back to you within 24 hours. In the meantime, you can reach us at {primary_contact['email']} or {primary_contact['phone']}.

If this is urgent, please don't hesitate to call our emergency line: +1 (555) 911-HELP.

Best regards,
{self.assistant_name}"""
    
    def analyze_email_intent(self, sender: str, subject: str, body: str) -> Dict[str, Any]:
        """Analyze email to determine intent and appropriate response strategy."""
        
        inquiry_context = {
            "sender": sender,
            "subject": subject,
            "body": body
        }
        
        # Get response information
        response_info = tool_system.execute_tool("get_response_info", {
            "inquiry_context": inquiry_context
        })
        
        # Determine intent
        body_lower = body.lower()
        subject_lower = subject.lower()
        
        intent_analysis = {
            "primary_intent": "general_inquiry",
            "urgency": "normal",
            "category": "support",
            "requires_reply": True,
            "requires_forwarding": True,
            "disclosure_level": response_info.get("disclosure_level", "standard")
        }
        
        # Analyze intent
        if any(word in body_lower for word in ["urgent", "emergency", "asap", "immediately", "critical"]):
            intent_analysis["urgency"] = "high"
            intent_analysis["primary_intent"] = "urgent_request"
        
        elif any(word in body_lower for word in ["sales", "pricing", "quote", "buy", "purchase"]):
            intent_analysis["category"] = "sales"
            intent_analysis["primary_intent"] = "sales_inquiry"
        
        elif any(word in body_lower for word in ["job", "career", "hiring", "resume", "position"]):
            intent_analysis["category"] = "hr"
            intent_analysis["primary_intent"] = "job_inquiry"
        
        elif any(word in body_lower for word in ["manager", "executive", "ceo", "cto", "director"]):
            intent_analysis["category"] = "executive"
            intent_analysis["primary_intent"] = "executive_contact"
        
        elif any(word in body_lower for word in ["thank", "thanks", "appreciate", "grateful"]):
            intent_analysis["primary_intent"] = "appreciation"
            intent_analysis["requires_forwarding"] = False
        
        elif any(word in body_lower for word in ["complaint", "issue", "problem", "disappointed"]):
            intent_analysis["category"] = "support"
            intent_analysis["primary_intent"] = "complaint"
            intent_analysis["urgency"] = "high"
        
        return {
            "intent": intent_analysis,
            "response_info": response_info
        }
    
    def should_reply(self, intent_analysis: Dict[str, Any]) -> bool:
        """Determine if the email should receive a reply."""
        
        intent = intent_analysis["intent"]
        
        # Always reply to urgent requests
        if intent["urgency"] == "high":
            return True
        
        # Reply to most inquiries except spam
        if intent["primary_intent"] in ["urgent_request", "sales_inquiry", "job_inquiry", 
                                       "executive_contact", "appreciation", "complaint"]:
            return True
        
        # Default to replying
        return intent["requires_reply"]
    
    def get_forwarding_recipient(self, intent_analysis: Dict[str, Any]) -> Optional[str]:
        """Determine who to forward the email to using private knowledge base."""
        
        intent = intent_analysis["intent"]
        
        if not intent["requires_forwarding"]:
            return None
        
        # Map intent categories to inquiry types
        category_mapping = {
            "sales": "sales_inquiries",
            "support": "support_requests", 
            "technical": "technical_issues",
            "executive": "executive_requests",
            "hr": "hr_inquiries"
        }
        
        inquiry_type = category_mapping.get(intent["category"], "support_requests")
        
        # Check if urgent matters need special handling
        if intent["urgency"] == "high":
            inquiry_type = "urgent_matters"
        
        # Get best employee for this inquiry type
        best_employee = private_kb.get_best_employee_for_inquiry(inquiry_type)
        
        if best_employee:
            return best_employee
        
        # Fallback to original logic
        response_info = intent_analysis["response_info"]
        contacts = response_info.get("contacts", [])
        
        if contacts:
            return contacts[0]["info"]["email"]
        
        return "support@techcorp.com"

# Global instance
ai_assistant = AIEmailAssistant()
