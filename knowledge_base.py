#!/usr/bin/env python3
"""
Knowledge Base and Tool System for AI Email Assistant
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from employee_data import employee_db, SecurityLevel

class KnowledgeBase:
    """Company knowledge base with controlled information disclosure."""
    
    def __init__(self):
        self.company_info = {
            "name": "TechCorp Solutions",
            "website": "https://techcorp.com",
            "industry": "Technology Solutions",
            "founded": "2015",
            "headquarters": "San Francisco, CA",
            "mission": "Empowering businesses with innovative technology solutions",
            "values": ["Innovation", "Integrity", "Customer Focus", "Excellence"]
        }
        
        self.contacts = {
            "executive": {
                "ceo": {
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@techcorp.com",
                    "phone": "+1 (555) 100-0001",
                    "title": "Chief Executive Officer",
                    "disclosure_level": "restricted"
                },
                "cto": {
                    "name": "Michael Chen",
                    "email": "michael.chen@techcorp.com", 
                    "phone": "+1 (555) 100-0002",
                    "title": "Chief Technology Officer",
                    "disclosure_level": "restricted"
                }
            },
            "management": {
                "vp_sales": {
                    "name": "David Rodriguez",
                    "email": "david.rodriguez@techcorp.com",
                    "phone": "+1 (555) 200-0001",
                    "title": "VP of Sales",
                    "disclosure_level": "public"
                },
                "vp_marketing": {
                    "name": "Lisa Wang",
                    "email": "lisa.wang@techcorp.com",
                    "phone": "+1 (555) 200-0002", 
                    "title": "VP of Marketing",
                    "disclosure_level": "public"
                },
                "hr_director": {
                    "name": "Jennifer Smith",
                    "email": "jennifer.smith@techcorp.com",
                    "phone": "+1 (555) 200-0003",
                    "title": "Director of Human Resources",
                    "disclosure_level": "public"
                }
            },
            "support": {
                "support_manager": {
                    "name": "Robert Kim",
                    "email": "robert.kim@techcorp.com",
                    "phone": "+1 (555) 300-0001",
                    "title": "Support Manager",
                    "disclosure_level": "public"
                },
                "technical_lead": {
                    "name": "Amanda Taylor",
                    "email": "amanda.taylor@techcorp.com",
                    "phone": "+1 (555) 300-0002",
                    "title": "Technical Lead",
                    "disclosure_level": "public"
                }
            }
        }
        
        self.services = {
            "cloud_solutions": {
                "name": "Cloud Solutions",
                "description": "Scalable cloud infrastructure and migration services",
                "pricing": "Starting at $5,000/month",
                "contact": "david.rodriguez@techcorp.com",
                "disclosure_level": "public"
            },
            "ai_consulting": {
                "name": "AI Consulting",
                "description": "Artificial intelligence strategy and implementation",
                "pricing": "Custom pricing based on project scope",
                "contact": "michael.chen@techcorp.com",
                "disclosure_level": "restricted"
            },
            "support_services": {
                "name": "Support Services",
                "description": "24/7 technical support and maintenance",
                "pricing": "Starting at $2,000/month",
                "contact": "robert.kim@techcorp.com",
                "disclosure_level": "public"
            }
        }
        
        self.policies = {
            "privacy": "We maintain strict confidentiality and data protection standards",
            "response_time": "We respond to all inquiries within 24 hours",
            "emergency": "For urgent matters, call our emergency line: +1 (555) 911-HELP",
            "disclosure": "Information sharing is based on inquiry type and authorization level"
        }

    def get_contact_info(self, contact_type: str, inquiry_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get contact information based on inquiry context and disclosure rules."""
        
        # Determine disclosure level based on inquiry
        disclosure_level = self._determine_disclosure_level(inquiry_context)
        
        # Convert to SecurityLevel enum
        if disclosure_level == "high":
            security_level = SecurityLevel.CONFIDENTIAL
        elif disclosure_level == "standard":
            security_level = SecurityLevel.TRUSTED
        else:
            security_level = SecurityLevel.PUBLIC
        
        # Search employees with security level filtering
        if contact_type in ["executive", "management", "support"]:
            # Map contact types to departments
            department_map = {
                "executive": "Executive",
                "management": ["Sales", "Marketing", "HR"],
                "support": ["Support", "Engineering"]
            }
            
            if contact_type == "executive":
                employees = employee_db.get_department_employees("Executive", security_level, inquiry_context)
            elif contact_type == "management":
                employees = []
                for dept in department_map["management"]:
                    employees.extend(employee_db.get_department_employees(dept, security_level, inquiry_context))
            else:  # support
                employees = []
                for dept in department_map["support"]:
                    employees.extend(employee_db.get_department_employees(dept, security_level, inquiry_context))
            
            if employees:
                # Return the first employee found
                emp = employees[0]
                return {
                    "name": emp["name"],
                    "email": emp.get("company_email", emp.get("direct_email", "")),
                    "phone": emp.get("phone", ""),
                    "title": emp["title"],
                    "department": emp.get("department", ""),
                    "disclosure_level": security_level.value,
                    "security_level": security_level.value
                }
        
        # Fallback to general contact
        return {
            "name": "Support Team",
            "email": "support@techcorp.com",
            "phone": "+1 (555) 123-4567",
            "title": "Customer Support",
            "disclosure_level": "public",
            "security_level": "public"
        }

    def get_service_info(self, service_name: str, inquiry_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get service information with appropriate disclosure."""
        
        disclosure_level = self._determine_disclosure_level(inquiry_context)
        
        if service_name in self.services:
            service = self.services[service_name]
            if service["disclosure_level"] == "public" or disclosure_level == "high":
                return service
        
        return None

    def get_company_info(self, inquiry_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get company information with appropriate disclosure."""
        
        disclosure_level = self._determine_disclosure_level(inquiry_context)
        
        if disclosure_level == "high":
            return self.company_info
        else:
            # Return basic public information
            return {
                "name": self.company_info["name"],
                "website": self.company_info["website"],
                "industry": self.company_info["industry"],
                "mission": self.company_info["mission"]
            }

    def _determine_disclosure_level(self, inquiry_context: Dict[str, Any]) -> str:
        """Determine appropriate disclosure level based on inquiry context."""
        
        # High disclosure indicators
        high_disclosure_keywords = [
            "partnership", "investment", "acquisition", "merger", "board", "investor",
            "enterprise", "enterprise client", "large contract", "strategic"
        ]
        
        # Check sender domain for trusted partners
        sender_email = inquiry_context.get("sender", "").lower()
        trusted_domains = ["@techcorp.com", "@partner.com", "@investor.com"]
        
        if any(domain in sender_email for domain in trusted_domains):
            return "high"
        
        # Check inquiry content
        inquiry_text = (inquiry_context.get("subject", "") + " " + 
                       inquiry_context.get("body", "")).lower()
        
        if any(keyword in inquiry_text for keyword in high_disclosure_keywords):
            return "high"
        
        # Check for urgent/emergency
        urgent_keywords = ["urgent", "emergency", "asap", "immediately", "critical"]
        if any(keyword in inquiry_text for keyword in urgent_keywords):
            return "high"
        
        return "standard"

    def search_contacts(self, query: str, inquiry_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search contacts based on query with security level filtering."""
        
        # Determine security level based on inquiry context
        disclosure_level = self._determine_disclosure_level(inquiry_context or {})
        
        if disclosure_level == "high":
            security_level = SecurityLevel.CONFIDENTIAL
        elif disclosure_level == "standard":
            security_level = SecurityLevel.TRUSTED
        else:
            security_level = SecurityLevel.PUBLIC
        
        # Search employees with security level filtering
        employees = employee_db.search_employees(query, security_level, inquiry_context)
        
        results = []
        for emp in employees:
            results.append({
                "category": emp.get("department", "Unknown"),
                "role": emp.get("title", "Unknown"),
                "info": {
                    "name": emp["name"],
                    "email": emp.get("company_email", emp.get("direct_email", "")),
                    "phone": emp.get("phone", ""),
                    "title": emp["title"],
                    "department": emp.get("department", ""),
                    "disclosure_level": emp["security_level"],
                    "security_level": emp["security_level"]
                }
            })
        
        return results

    def get_appropriate_response_info(self, inquiry_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get all appropriate information for responding to an inquiry."""
        
        disclosure_level = self._determine_disclosure_level(inquiry_context)
        inquiry_text = (inquiry_context.get("subject", "") + " " + 
                       inquiry_context.get("body", "")).lower()
        
        response_info = {
            "disclosure_level": disclosure_level,
            "company_info": self.get_company_info(inquiry_context),
            "contacts": [],
            "services": [],
            "policies": self.policies
        }
        
        # Determine relevant contacts
        if any(word in inquiry_text for word in ["sales", "pricing", "quote", "buy"]):
            contact = self.get_contact_info("management", inquiry_context)
            if contact:
                response_info["contacts"].append({"type": "sales", "info": contact})
        
        if any(word in inquiry_text for word in ["support", "help", "issue", "problem"]):
            contact = self.get_contact_info("support", inquiry_context)
            if contact:
                response_info["contacts"].append({"type": "support", "info": contact})
        
        if any(word in inquiry_text for word in ["job", "career", "hiring", "resume"]):
            contact = self.get_contact_info("management", inquiry_context)
            if contact:
                response_info["contacts"].append({"type": "hr", "info": contact})
        
        if any(word in inquiry_text for word in ["manager", "executive", "ceo", "cto"]):
            contact = self.get_contact_info("executive", inquiry_context)
            if contact:
                response_info["contacts"].append({"type": "executive", "info": contact})
        
        # Determine relevant services
        if any(word in inquiry_text for word in ["cloud", "infrastructure", "migration"]):
            service = self.get_service_info("cloud_solutions", inquiry_context)
            if service:
                response_info["services"].append(service)
        
        if any(word in inquiry_text for word in ["ai", "artificial intelligence", "machine learning"]):
            service = self.get_service_info("ai_consulting", inquiry_context)
            if service:
                response_info["services"].append(service)
        
        if any(word in inquiry_text for word in ["support", "maintenance", "technical"]):
            service = self.get_service_info("support_services", inquiry_context)
            if service:
                response_info["services"].append(service)
        
        return response_info

class ToolSystem:
    """Tool system for AI assistant to access various resources."""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for the AI assistant."""
        
        return [
            {
                "name": "get_contact_info",
                "description": "Get contact information for specific roles or departments",
                "parameters": {
                    "contact_type": "string (executive, management, support)",
                    "inquiry_context": "object with sender, subject, body"
                }
            },
            {
                "name": "get_service_info", 
                "description": "Get information about company services",
                "parameters": {
                    "service_name": "string (cloud_solutions, ai_consulting, support_services)",
                    "inquiry_context": "object with sender, subject, body"
                }
            },
            {
                "name": "get_company_info",
                "description": "Get company information with appropriate disclosure",
                "parameters": {
                    "inquiry_context": "object with sender, subject, body"
                }
            },
            {
                "name": "search_contacts",
                "description": "Search for contacts by name, title, or role",
                "parameters": {
                    "query": "string search term"
                }
            },
            {
                "name": "get_response_info",
                "description": "Get all appropriate information for responding to an inquiry",
                "parameters": {
                    "inquiry_context": "object with sender, subject, body"
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with given parameters."""
        
        if tool_name == "get_contact_info":
            return self.kb.get_contact_info(
                parameters.get("contact_type"), 
                parameters.get("inquiry_context", {})
            )
        
        elif tool_name == "get_service_info":
            return self.kb.get_service_info(
                parameters.get("service_name"),
                parameters.get("inquiry_context", {})
            )
        
        elif tool_name == "get_company_info":
            return self.kb.get_company_info(
                parameters.get("inquiry_context", {})
            )
        
        elif tool_name == "search_contacts":
            return self.kb.search_contacts(
                parameters.get("query", ""),
                parameters.get("inquiry_context", {})
            )
        
        elif tool_name == "get_response_info":
            return self.kb.get_appropriate_response_info(
                parameters.get("inquiry_context", {})
            )
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}

# Global instances
knowledge_base = KnowledgeBase()
tool_system = ToolSystem(knowledge_base)
