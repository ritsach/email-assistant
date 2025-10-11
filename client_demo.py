#!/usr/bin/env python3
"""
Email Assistant API Client Demo
"""

import requests
import json
from datetime import datetime

class EmailAssistantClient:
    """Client for Email Assistant API"""
    
    def __init__(self, base_url="http://localhost:5001", api_key="your-secret-api-key-here"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def health_check(self):
        """Check if the API server is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_employees(self, security_level="public", department=""):
        """List employees with security level filtering"""
        params = {"security_level": security_level}
        if department:
            params["department"] = department
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/employees", 
                                  headers=self.headers, params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_employee(self, employee_id, security_level="public"):
        """Get specific employee information"""
        params = {"security_level": security_level}
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/employees/{employee_id}",
                                  headers=self.headers, params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search_employees(self, query, security_level="public", context=None):
        """Search employees with security level filtering"""
        data = {
            "query": query,
            "security_level": security_level
        }
        if context:
            data["context"] = context
        
        try:
            response = requests.post(f"{self.base_url}/api/v1/employees/search",
                                   headers=self.headers, json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_email(self, sender, subject, body):
        """Analyze an email for intent and generate response"""
        data = {
            "email": {
                "sender": sender,
                "subject": subject,
                "body": body
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/v1/emails/analyze",
                                   headers=self.headers, json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search_knowledge(self, query, security_level="public", context=None):
        """Search the knowledge base"""
        data = {
            "query": query,
            "security_level": security_level
        }
        if context:
            data["context"] = context
        
        try:
            response = requests.post(f"{self.base_url}/api/v1/knowledge/search",
                                   headers=self.headers, json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_emails(self):
        """Process unread emails"""
        try:
            response = requests.post(f"{self.base_url}/api/v1/emails/process",
                                   headers=self.headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def demo_api():
    """Demonstrate API functionality"""
    
    print("🚀 Email Assistant API Client Demo")
    print("=" * 60)
    
    # Initialize client
    client = EmailAssistantClient()
    
    # Health check
    print("1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Version: {health.get('version', 'unknown')}")
    print()
    
    # List employees
    print("2. List Employees (Public Level):")
    employees = client.list_employees()
    if "employees" in employees:
        print(f"   Found {employees['count']} employees")
        for emp in employees["employees"][:3]:  # Show first 3
            print(f"   - {emp['name']} ({emp['title']}) - {emp['company_email']}")
    print()
    
    # Get specific employee
    print("3. Get Specific Employee:")
    emp = client.get_employee("EMP001")
    if "employee" in emp:
        emp_data = emp["employee"]
        print(f"   Name: {emp_data['name']}")
        print(f"   Title: {emp_data['title']}")
        print(f"   Email: {emp_data['company_email']}")
        print(f"   Department: {emp_data['department']}")
    print()
    
    # Search employees
    print("4. Search Employees:")
    search_results = client.search_employees("Sarah")
    if "employees" in search_results:
        print(f"   Found {search_results['count']} employees for 'Sarah'")
        for emp in search_results["employees"]:
            print(f"   - {emp['name']} ({emp['title']})")
    print()
    
    # Analyze email
    print("5. Analyze Email:")
    analysis = client.analyze_email(
        sender="customer@example.com",
        subject="Question about your services",
        body="Hi, I'm interested in learning more about your AI consulting services. Can you send me more information?"
    )
    if "analysis" in analysis:
        intent = analysis["analysis"]["intent"]
        print(f"   Intent: {intent['primary_intent']}")
        print(f"   Category: {intent['category']}")
        print(f"   Urgency: {intent['urgency']}")
        print(f"   Should Reply: {analysis['should_reply']}")
        if analysis['should_reply']:
            print(f"   Reply Preview: {analysis['reply_text'][:100]}...")
    print()
    
    # Search knowledge base
    print("6. Search Knowledge Base:")
    knowledge = client.search_knowledge("CEO")
    if "employees" in knowledge:
        print(f"   Found {len(knowledge['employees'])} employees for 'CEO'")
        for emp in knowledge["employees"]:
            print(f"   - {emp['name']} ({emp['title']})")
    print()
    
    # Test different security levels
    print("7. Security Level Testing:")
    for level in ["public", "trusted", "confidential"]:
        emp = client.get_employee("EMP001", security_level=level)
        if "employee" in emp:
            emp_data = emp["employee"]
            print(f"   {level.upper()}: {emp_data['name']} - {emp_data.get('phone', 'No phone')}")
    print()
    
    print("✅ API Demo Complete!")
    print("\nAvailable Endpoints:")
    print("• GET  /health")
    print("• GET  /api/v1/employees")
    print("• GET  /api/v1/employees/{id}")
    print("• POST /api/v1/employees/search")
    print("• POST /api/v1/emails/analyze")
    print("• POST /api/v1/knowledge/search")
    print("• POST /api/v1/emails/process")

if __name__ == "__main__":
    demo_api()
