#!/usr/bin/env python3
"""
Employee Data Management with Three-Level Security System
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json
import os
from datetime import datetime

class SecurityLevel(Enum):
    """Three levels of information security"""
    PUBLIC = "public"           # Can be shared with anyone
    TRUSTED = "trusted"        # Can be shared with trusted partners/clients
    CONFIDENTIAL = "confidential"  # Cannot be shared externally

class Employee:
    """Employee data structure with security levels"""
    
    def __init__(self, employee_id: str, name: str, title: str, email: str, 
                 phone: str = "", department: str = "", manager: str = ""):
        self.employee_id = employee_id
        self.name = name
        self.title = title
        self.email = email
        self.phone = phone
        self.department = department
        self.manager = manager
        
        # Security levels for different types of information
        self.security_levels = {
            "contact_info": SecurityLevel.PUBLIC,
            "role_details": SecurityLevel.PUBLIC,
            "direct_contact": SecurityLevel.TRUSTED,
            "personal_info": SecurityLevel.CONFIDENTIAL,
            "internal_processes": SecurityLevel.CONFIDENTIAL,
            "salary_info": SecurityLevel.CONFIDENTIAL
        }
        
        # Information categorized by security level
        self.public_info = {
            "name": name,
            "title": title,
            "department": department,
            "company_email": email
        }
        
        self.trusted_info = {
            "phone": phone,
            "direct_email": email,
            "manager": manager,
            "availability": "Business hours: 9 AM - 5 PM EST"
        }
        
        self.confidential_info = {
            "employee_id": employee_id,
            "salary_range": "",
            "performance_notes": "",
            "internal_projects": [],
            "personal_phone": "",
            "home_address": "",
            "emergency_contact": ""
        }
    
    def get_info_for_level(self, security_level: SecurityLevel, 
                          inquiry_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get employee information based on security level and inquiry context"""
        
        # Determine if requester is trusted
        is_trusted = self._is_trusted_requester(inquiry_context or {})
        
        if security_level == SecurityLevel.PUBLIC:
            return self.public_info.copy()
        
        elif security_level == SecurityLevel.TRUSTED and is_trusted:
            info = self.public_info.copy()
            info.update(self.trusted_info)
            return info
        
        elif security_level == SecurityLevel.CONFIDENTIAL and is_trusted:
            info = self.public_info.copy()
            info.update(self.trusted_info)
            # Only include non-sensitive confidential info
            safe_confidential = {
                "employee_id": self.confidential_info["employee_id"],
                "internal_projects": [p for p in self.confidential_info["internal_projects"] 
                                    if not p.get("sensitive", False)]
            }
            info.update(safe_confidential)
            return info
        
        else:
            # Return minimal public info
            return {
                "name": self.name,
                "title": self.title,
                "department": self.department
            }
    
    def _is_trusted_requester(self, inquiry_context: Dict[str, Any]) -> bool:
        """Determine if the requester is trusted based on context"""
        
        # Trusted domains
        trusted_domains = [
            "@techcorp.com",
            "@partner.com", 
            "@investor.com",
            "@client.com",
            "@berkeley.edu",
            "@laposte.net"
        ]
        
        # Trusted keywords in inquiry
        trusted_keywords = [
            "partnership", "collaboration", "contract", "agreement",
            "investment", "acquisition", "merger", "board",
            "enterprise", "enterprise client", "large contract", "strategic"
        ]
        
        sender_email = inquiry_context.get("sender", "").lower()
        inquiry_text = (inquiry_context.get("subject", "") + " " + 
                       inquiry_context.get("body", "")).lower()
        
        # Check trusted domains
        if any(domain in sender_email for domain in trusted_domains):
            return True
        
        # Check trusted keywords
        if any(keyword in inquiry_text for keyword in trusted_keywords):
            return True
        
        # Check for urgent/emergency (higher trust for urgent matters)
        urgent_keywords = ["urgent", "emergency", "asap", "immediately", "critical"]
        if any(keyword in inquiry_text for keyword in urgent_keywords):
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert employee to dictionary"""
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "title": self.title,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "manager": self.manager,
            "security_levels": {k: v.value for k, v in self.security_levels.items()},
            "public_info": self.public_info,
            "trusted_info": self.trusted_info,
            "confidential_info": self.confidential_info
        }

class EmployeeDatabase:
    """Database of employees with security management"""
    
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self._load_sample_data()
    
    def add_employee(self, employee: Employee):
        """Add employee to database"""
        self.employees[employee.employee_id] = employee
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        return self.employees.get(employee_id)
    
    def search_employees(self, query: str, security_level: SecurityLevel = SecurityLevel.PUBLIC,
                       inquiry_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search employees with security level filtering"""
        
        results = []
        query_lower = query.lower()
        
        for employee in self.employees.values():
            # Check if employee matches search query
            if (query_lower in employee.name.lower() or 
                query_lower in employee.title.lower() or
                query_lower in employee.department.lower()):
                
                # Get information based on security level
                employee_info = employee.get_info_for_level(security_level, inquiry_context)
                
                # Add security level indicator
                employee_info["security_level"] = security_level.value
                employee_info["employee_id"] = employee.employee_id
                
                results.append(employee_info)
        
        return results
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email address"""
        for employee in self.employees.values():
            if employee.email.lower() == email.lower():
                return employee
        return None
    
    def get_department_employees(self, department: str, security_level: SecurityLevel = SecurityLevel.PUBLIC,
                               inquiry_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all employees in a department"""
        
        results = []
        
        for employee in self.employees.values():
            if employee.department.lower() == department.lower():
                employee_info = employee.get_info_for_level(security_level, inquiry_context)
                employee_info["security_level"] = security_level.value
                employee_info["employee_id"] = employee.employee_id
                results.append(employee_info)
        
        return results
    
    def _load_sample_data(self):
        """Load sample employee data"""
        
        # Executive Team
        self.add_employee(Employee(
            employee_id="EMP001",
            name="Sarah Johnson",
            title="Chief Executive Officer",
            email="sarah.johnson@techcorp.com",
            phone="+1 (555) 100-0001",
            department="Executive",
            manager="Board of Directors"
        ))
        
        self.add_employee(Employee(
            employee_id="EMP002",
            name="Michael Chen",
            title="Chief Technology Officer",
            email="michael.chen@techcorp.com",
            phone="+1 (555) 100-0002",
            department="Executive",
            manager="Sarah Johnson"
        ))
        
        # Management Team
        self.add_employee(Employee(
            employee_id="EMP003",
            name="David Rodriguez",
            title="VP of Sales",
            email="david.rodriguez@techcorp.com",
            phone="+1 (555) 200-0001",
            department="Sales",
            manager="Sarah Johnson"
        ))
        
        self.add_employee(Employee(
            employee_id="EMP004",
            name="Lisa Wang",
            title="VP of Marketing",
            email="lisa.wang@techcorp.com",
            phone="+1 (555) 200-0002",
            department="Marketing",
            manager="Sarah Johnson"
        ))
        
        self.add_employee(Employee(
            employee_id="EMP005",
            name="Jennifer Smith",
            title="Director of Human Resources",
            email="jennifer.smith@techcorp.com",
            phone="+1 (555) 200-0003",
            department="HR",
            manager="Sarah Johnson"
        ))
        
        # Support Team
        self.add_employee(Employee(
            employee_id="EMP006",
            name="Robert Kim",
            title="Support Manager",
            email="robert.kim@techcorp.com",
            phone="+1 (555) 300-0001",
            department="Support",
            manager="Michael Chen"
        ))
        
        self.add_employee(Employee(
            employee_id="EMP007",
            name="Amanda Taylor",
            title="Technical Lead",
            email="amanda.taylor@techcorp.com",
            phone="+1 (555) 300-0002",
            department="Engineering",
            manager="Michael Chen"
        ))
        
        # External Contacts (from original CONTACTS)
        self.add_employee(Employee(
            employee_id="EMP008",
            name="Adil Al",
            title="Sales Representative",
            email="ads.al@laposte.net",
            phone="+1 (555) 400-0001",
            department="Sales",
            manager="David Rodriguez"
        ))
        
        self.add_employee(Employee(
            employee_id="EMP009",
            name="Victor Sana",
            title="Support Specialist",
            email="victor.sana@berkeley.edu",
            phone="+1 (555) 400-0002",
            department="Support",
            manager="Robert Kim"
        ))
        
        self.add_employee(Employee(
            employee_id="EMP010",
            name="Idris Houiralami",
            title="Technical Specialist",
            email="idris.houiralami@berkeley.edu",
            phone="+1 (555) 400-0003",
            department="Engineering",
            manager="Amanda Taylor"
        ))
        
        # Add confidential information
        self._add_confidential_data()
    
    def _add_confidential_data(self):
        """Add confidential information to employees"""
        
        # CEO confidential info
        ceo = self.employees["EMP001"]
        ceo.confidential_info.update({
            "salary_range": "$300,000 - $400,000",
            "performance_notes": "Excellent leadership, strong strategic vision",
            "internal_projects": [
                {"name": "Strategic Partnership", "sensitive": True},
                {"name": "Product Roadmap", "sensitive": False}
            ],
            "personal_phone": "+1 (555) 999-0001",
            "home_address": "123 Executive Lane, San Francisco, CA",
            "emergency_contact": "John Johnson (Spouse) +1 (555) 999-0002"
        })
        
        # CTO confidential info
        cto = self.employees["EMP002"]
        cto.confidential_info.update({
            "salary_range": "$250,000 - $350,000",
            "performance_notes": "Technical excellence, innovation leader",
            "internal_projects": [
                {"name": "AI Platform Development", "sensitive": True},
                {"name": "Security Audit", "sensitive": False}
            ],
            "personal_phone": "+1 (555) 999-0003",
            "home_address": "456 Tech Street, Palo Alto, CA",
            "emergency_contact": "Maria Chen (Spouse) +1 (555) 999-0004"
        })
        
        # VP Sales confidential info
        vp_sales = self.employees["EMP003"]
        vp_sales.confidential_info.update({
            "salary_range": "$200,000 - $300,000",
            "performance_notes": "Strong sales performance, client relationships",
            "internal_projects": [
                {"name": "Enterprise Sales Strategy", "sensitive": True},
                {"name": "Client Onboarding", "sensitive": False}
            ],
            "personal_phone": "+1 (555) 999-0005",
            "home_address": "789 Sales Avenue, San Jose, CA",
            "emergency_contact": "Ana Rodriguez (Spouse) +1 (555) 999-0006"
        })
    
    def save_to_file(self, filename: str):
        """Save employee database to file"""
        data = {
            "employees": {emp_id: emp.to_dict() for emp_id, emp in self.employees.items()},
            "last_updated": datetime.utcnow().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str):
        """Load employee database from file"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.employees = {}
            for emp_id, emp_data in data["employees"].items():
                emp = Employee(
                    employee_id=emp_data["employee_id"],
                    name=emp_data["name"],
                    title=emp_data["title"],
                    email=emp_data["email"],
                    phone=emp_data["phone"],
                    department=emp_data["department"],
                    manager=emp_data["manager"]
                )
                emp.security_levels = {k: SecurityLevel(v) for k, v in emp_data["security_levels"].items()}
                emp.public_info = emp_data["public_info"]
                emp.trusted_info = emp_data["trusted_info"]
                emp.confidential_info = emp_data["confidential_info"]
                
                self.employees[emp_id] = emp

# Global instance
employee_db = EmployeeDatabase()
