#!/usr/bin/env python3
"""
Private Knowledge Base Manager for Employee Information
Handles private employee data with disclosure controls
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class PrivateKnowledgeBase:
    """Manages private employee information with disclosure controls."""
    
    def __init__(self, database_path: str = "private_employee_database.json"):
        self.database_path = Path(database_path)
        self._data = None
        self._load_database()
    
    def _load_database(self):
        """Load the private employee database."""
        try:
            if self.database_path.exists():
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            else:
                print(f"Warning: Private database not found at {self.database_path}")
                self._data = {"employees": {}, "company_context": {}, "disclosure_policies": {}, "forwarding_rules": {}}
        except Exception as e:
            print(f"Error loading private database: {e}")
            self._data = {"employees": {}, "company_context": {}, "disclosure_policies": {}, "forwarding_rules": {}}
    
    def get_employee_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get employee information by email address."""
        return self._data.get("employees", {}).get(email)
    
    def get_employee_info(self, email: str, disclosure_level: str = "public") -> Optional[Dict[str, Any]]:
        """Get employee information filtered by disclosure level."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return None
        
        # Get allowed fields for this disclosure level
        allowed_fields = employee.get("disclosure_levels", {}).get(disclosure_level, [])
        
        # Filter the employee data
        filtered_info = {}
        for field in allowed_fields:
            if field in employee:
                filtered_info[field] = employee[field]
            elif field in employee.get("personal_info", {}):
                filtered_info[field] = employee["personal_info"][field]
            elif field in employee.get("contact_info", {}):
                filtered_info[field] = employee["contact_info"][field]
            elif field in employee.get("professional", {}):
                filtered_info[field] = employee["professional"][field]
        
        return filtered_info
    
    def get_employee_skills(self, email: str) -> List[str]:
        """Get employee skills."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return []
        return employee.get("professional", {}).get("skills", [])
    
    def get_employee_responsibilities(self, email: str) -> List[str]:
        """Get employee responsibilities."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return []
        return employee.get("professional", {}).get("responsibilities", [])
    
    def get_employee_knowledge_areas(self, email: str) -> List[str]:
        """Get employee knowledge areas."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return []
        return employee.get("professional", {}).get("knowledge_areas", [])
    
    def get_employee_role(self, email: str) -> Optional[str]:
        """Get employee role."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return None
        return employee.get("role")
    
    def get_employee_department(self, email: str) -> Optional[str]:
        """Get employee department."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return None
        return employee.get("department")
    
    def get_employee_forwarding_rules(self, email: str) -> Dict[str, str]:
        """Get employee email forwarding rules."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return {}
        return employee.get("email_forwarding_rules", {})
    
    def should_forward_to_employee(self, email: str, inquiry_type: str) -> bool:
        """Check if an inquiry should be forwarded to a specific employee."""
        forwarding_rules = self.get_employee_forwarding_rules(email)
        rule = forwarding_rules.get(inquiry_type, "none")
        return rule in ["primary", "secondary"]
    
    def get_best_employee_for_inquiry(self, inquiry_type: str) -> Optional[str]:
        """Get the best employee email for a specific inquiry type."""
        forwarding_rules = self._data.get("forwarding_rules", {})
        employees = forwarding_rules.get(inquiry_type, [])
        
        if not employees:
            return None
        
        # Return the first employee (primary)
        return employees[0] if employees else None
    
    def get_employee_contact_info(self, email: str, disclosure_level: str = "public") -> Dict[str, Any]:
        """Get employee contact information based on disclosure level."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return {}
        
        contact_info = employee.get("contact_info", {})
        allowed_fields = employee.get("disclosure_levels", {}).get(disclosure_level, [])
        
        filtered_contact = {}
        for field in allowed_fields:
            if field in contact_info:
                filtered_contact[field] = contact_info[field]
        
        return filtered_contact
    
    def search_employees_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Search employees by skill."""
        results = []
        for email, employee in self._data.get("employees", {}).items():
            skills = employee.get("professional", {}).get("skills", [])
            if skill.lower() in [s.lower() for s in skills]:
                results.append({
                    "email": email,
                    "name": employee.get("name"),
                    "role": employee.get("role"),
                    "department": employee.get("department"),
                    "skills": skills
                })
        return results
    
    def search_employees_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Search employees by role."""
        results = []
        for email, employee in self._data.get("employees", {}).items():
            if role.lower() in employee.get("role", "").lower():
                results.append({
                    "email": email,
                    "name": employee.get("name"),
                    "role": employee.get("role"),
                    "department": employee.get("department")
                })
        return results
    
    def get_company_context(self) -> Dict[str, Any]:
        """Get company context information."""
        return self._data.get("company_context", {})
    
    def get_disclosure_policies(self) -> Dict[str, str]:
        """Get disclosure policies."""
        return self._data.get("disclosure_policies", {})
    
    def get_all_employees(self, disclosure_level: str = "public") -> List[Dict[str, Any]]:
        """Get all employees with filtered information."""
        employees = []
        for email, employee in self._data.get("employees", {}).items():
            filtered_info = self.get_employee_info(email, disclosure_level)
            if filtered_info:
                filtered_info["email"] = email
                employees.append(filtered_info)
        return employees
    
    def get_employee_summary(self, email: str) -> Dict[str, Any]:
        """Get a summary of employee information for email forwarding decisions."""
        employee = self.get_employee_by_email(email)
        if not employee:
            return {}
        
        return {
            "name": employee.get("name"),
            "role": employee.get("role"),
            "department": employee.get("department"),
            "title": employee.get("title"),
            "skills": employee.get("professional", {}).get("skills", []),
            "responsibilities": employee.get("professional", {}).get("responsibilities", []),
            "knowledge_areas": employee.get("professional", {}).get("knowledge_areas", []),
            "forwarding_rules": employee.get("email_forwarding_rules", {}),
            "work_phone": employee.get("contact_info", {}).get("work_phone"),
            "office_location": employee.get("contact_info", {}).get("office_location")
        }
    
    def determine_disclosure_level(self, inquiry_context: Dict[str, Any]) -> str:
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
            return "restricted"
        
        # Check inquiry content
        inquiry_text = (inquiry_context.get("subject", "") + " " + 
                       inquiry_context.get("body", "")).lower()
        
        if any(keyword in inquiry_text for keyword in high_disclosure_keywords):
            return "restricted"
        
        # Check for urgent/emergency
        urgent_keywords = ["urgent", "emergency", "asap", "immediately", "critical"]
        if any(keyword in inquiry_text for keyword in urgent_keywords):
            return "restricted"
        
        return "public"

# Global instance
private_kb = PrivateKnowledgeBase()
