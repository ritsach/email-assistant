#!/usr/bin/env python3
"""
Verify that contacts are properly linked to employees
"""

from employee_data import employee_db
from email_assistant import CONTACTS, get_employee_contact

def verify_contact_linking():
    """Verify that contacts are linked to employees"""
    
    print("🔗 Verifying Contact-Employee Linking")
    print("=" * 60)
    
    # Check current CONTACTS configuration
    print("📧 Current CONTACTS Configuration:")
    for contact_type, email in CONTACTS.items():
        print(f"  {contact_type}: {email}")
    
    print("\n👥 Employee Database:")
    
    # Check if each contact email exists in employee database
    for contact_type, email in CONTACTS.items():
        employee = employee_db.get_employee_by_email(email)
        if employee:
            print(f"✅ {contact_type} ({email}) -> {employee.name} ({employee.title})")
            print(f"   Department: {employee.department}")
            print(f"   Employee ID: {employee.employee_id}")
        else:
            print(f"❌ {contact_type} ({email}) -> NOT FOUND in employee database")
    
    print("\n🏢 Department-based Contact Resolution:")
    
    # Test department-based contact resolution
    departments = ["Sales", "Support", "Engineering"]
    for dept in departments:
        employees = employee_db.get_department_employees(dept)
        if employees:
            primary_contact = employees[0]
            print(f"  {dept}: {primary_contact['name']} ({primary_contact['title']})")
            print(f"    Email: {primary_contact.get('company_email', primary_contact.get('direct_email', 'N/A'))}")
            print(f"    Employee ID: {primary_contact['employee_id']}")
        else:
            print(f"  {dept}: No employees found")
    
    print("\n🔍 Testing Contact Resolution Function:")
    
    # Test the get_employee_contact function
    contact_types = ["sales", "support", "technical"]
    for contact_type in contact_types:
        email = get_employee_contact(contact_type)
        employee = employee_db.get_employee_by_email(email)
        if employee:
            print(f"  {contact_type}: {email} -> {employee.name} ({employee.title})")
        else:
            print(f"  {contact_type}: {email} -> NOT FOUND in employee database")
    
    print("\n📊 Summary:")
    
    # Count total employees
    total_employees = len(employee_db.employees)
    print(f"  Total employees in database: {total_employees}")
    
    # Count employees by department
    departments = {}
    for emp in employee_db.employees.values():
        dept = emp.department
        departments[dept] = departments.get(dept, 0) + 1
    
    print("  Employees by department:")
    for dept, count in departments.items():
        print(f"    {dept}: {count} employees")
    
    # Check if all contacts are linked
    linked_contacts = 0
    total_contacts = len(CONTACTS)
    
    for email in CONTACTS.values():
        if employee_db.get_employee_by_email(email):
            linked_contacts += 1
    
    print(f"  Linked contacts: {linked_contacts}/{total_contacts}")
    
    if linked_contacts == total_contacts:
        print("✅ All contacts are properly linked to employees!")
    else:
        print("⚠️  Some contacts are not linked to employees")

if __name__ == "__main__":
    verify_contact_linking()
