#!/usr/bin/env python3
"""
Email Assistant REST API Server
Provides REST endpoints for email processing functionality
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import threading
import time
from typing import Dict, List, Any

# Import the email assistant components
from email_assistant import process_emails, get_gmail_service, get_message_body, create_message, send_message
from ai_assistant import ai_assistant
from knowledge_base import knowledge_base
from employee_data import employee_db, SecurityLevel

app = Flask(__name__)
CORS(app)  # Enable CORS for web applications

# Configuration
API_KEY = os.environ.get('EMAIL_ASSISTANT_API_KEY', 'your-secret-api-key-here')
PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# In-memory storage for job tracking (use Redis/DB in production)
jobs = {}
job_lock = threading.Lock()

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def create_job_response(job_id: str, status: str, data: Dict = None) -> Dict:
    """Create a standardized job response"""
    response = {
        'job_id': job_id,
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data or {}
    }
    
    with job_lock:
        jobs[job_id] = response
    
    return response

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Email Assistant API Server',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': 'GET /health',
            'config': 'GET /api/v1/config (requires API key)',
            'employees': 'GET /api/v1/employees (requires API key)',
            'employee': 'GET /api/v1/employees/{id} (requires API key)',
            'search_employees': 'POST /api/v1/employees/search (requires API key)',
            'analyze_email': 'POST /api/v1/emails/analyze (requires API key)',
            'process_emails': 'POST /api/v1/emails/process (requires API key)',
            'send_email': 'POST /api/v1/emails/send (requires API key)',
            'search_knowledge': 'POST /api/v1/knowledge/search (requires API key)',
            'jobs': 'GET /api/v1/jobs (requires API key)',
            'job_status': 'GET /api/v1/jobs/{id} (requires API key)'
        },
        'authentication': 'Include X-API-Key header or api_key query parameter',
        'documentation': 'See API_DOCUMENTATION.md for detailed usage',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/v1/emails/process', methods=['POST'])
@require_api_key
def process_emails_endpoint():
    """Process unread emails"""
    try:
        job_id = str(uuid.uuid4())
        
        # Start processing in background thread
        def process_emails_background():
            try:
                # Capture the output by redirecting print statements
                import io
                import sys
                from contextlib import redirect_stdout
                
                output_buffer = io.StringIO()
                with redirect_stdout(output_buffer):
                    process_emails()
                
                output = output_buffer.getvalue()
                
                with job_lock:
                    jobs[job_id].update({
                        'status': 'completed',
                        'data': {
                            'output': output,
                            'processed_at': datetime.utcnow().isoformat()
                        }
                    })
                    
            except Exception as e:
                with job_lock:
                    jobs[job_id].update({
                        'status': 'failed',
                        'data': {
                            'error': str(e),
                            'failed_at': datetime.utcnow().isoformat()
                        }
                    })
        
        # Start background processing
        thread = threading.Thread(target=process_emails_background)
        thread.daemon = True
        thread.start()
        
        return jsonify(create_job_response(job_id, 'processing'))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/emails/analyze', methods=['POST'])
@require_api_key
def analyze_email():
    """Analyze a single email"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email data is required'}), 400
        
        email_data = data['email']
        sender = email_data.get('sender', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        # Use AI assistant to analyze the email
        intent_analysis = ai_assistant.analyze_email_intent(sender, subject, body)
        
        # Generate reply if needed
        reply_text = ""
        if ai_assistant.should_reply(intent_analysis):
            reply_text = ai_assistant.generate_intelligent_reply(sender, subject, body)
        
        # Get forwarding recipient
        recipient = ai_assistant.get_forwarding_recipient(intent_analysis)
        
        response = {
            'analysis': intent_analysis,
            'should_reply': ai_assistant.should_reply(intent_analysis),
            'reply_text': reply_text,
            'forward_to': recipient,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/emails/send', methods=['POST'])
@require_api_key
def send_email():
    """Send an email"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['to', 'subject', 'body']):
            return jsonify({'error': 'to, subject, and body are required'}), 400
        
        # Get Gmail service
        service = get_gmail_service()
        
        # Create and send message
        message = create_message(
            sender='me',
            to=data['to'],
            subject=data['subject'],
            message_text=data['body']
        )
        
        result = send_message(service, 'me', message)
        
        if result:
            return jsonify({
                'success': True,
                'message_id': result['id'],
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/knowledge/search', methods=['POST'])
@require_api_key
def search_knowledge():
    """Search the knowledge base"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        inquiry_context = data.get('context', {})
        security_level = data.get('security_level', 'public')
        
        # Convert string to SecurityLevel enum
        try:
            sec_level = SecurityLevel(security_level)
        except ValueError:
            sec_level = SecurityLevel.PUBLIC
        
        # Search contacts with security level filtering
        contacts = knowledge_base.search_contacts(query, inquiry_context)
        
        # Search employees directly
        employees = employee_db.search_employees(query, sec_level, inquiry_context)
        
        # Get response info
        response_info = knowledge_base.get_appropriate_response_info(inquiry_context)
        
        return jsonify({
            'contacts': contacts,
            'employees': employees,
            'response_info': response_info,
            'security_level': security_level,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/jobs/<job_id>', methods=['GET'])
@require_api_key
def get_job_status(job_id):
    """Get job status"""
    with job_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(jobs[job_id])

@app.route('/api/v1/jobs', methods=['GET'])
@require_api_key
def list_jobs():
    """List all jobs"""
    with job_lock:
        return jsonify({
            'jobs': list(jobs.values()),
            'count': len(jobs),
            'timestamp': datetime.utcnow().isoformat()
        })

@app.route('/api/v1/config', methods=['GET'])
@require_api_key
def get_config():
    """Get current configuration"""
    from email_assistant import CONTACTS
    
    return jsonify({
        'contacts': CONTACTS,
        'aws_region': 'us-east-1',
        'bedrock_model': 'anthropic.claude-sonnet-4-5-20250929-v1:0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/v1/config', methods=['PUT'])
@require_api_key
def update_config():
    """Update configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Configuration data is required'}), 400
        
        # In a production environment, you'd want to persist this configuration
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated (not persisted in this demo)',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/employees', methods=['GET'])
@require_api_key
def list_employees():
    """List employees with security level filtering"""
    try:
        security_level = request.args.get('security_level', 'public')
        department = request.args.get('department', '')
        inquiry_context = {}
        
        # Convert string to SecurityLevel enum
        try:
            sec_level = SecurityLevel(security_level)
        except ValueError:
            sec_level = SecurityLevel.PUBLIC
        
        if department:
            employees = employee_db.get_department_employees(department, sec_level, inquiry_context)
        else:
            # Get all employees (limited by security level)
            employees = []
            for emp_id, emp in employee_db.employees.items():
                emp_info = emp.get_info_for_level(sec_level, inquiry_context)
                emp_info["employee_id"] = emp_id
                emp_info["security_level"] = sec_level.value
                employees.append(emp_info)
        
        return jsonify({
            'employees': employees,
            'count': len(employees),
            'security_level': security_level,
            'department': department,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/employees/<employee_id>', methods=['GET'])
@require_api_key
def get_employee(employee_id):
    """Get specific employee information"""
    try:
        security_level = request.args.get('security_level', 'public')
        inquiry_context = {}
        
        # Convert string to SecurityLevel enum
        try:
            sec_level = SecurityLevel(security_level)
        except ValueError:
            sec_level = SecurityLevel.PUBLIC
        
        employee = employee_db.get_employee(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        employee_info = employee.get_info_for_level(sec_level, inquiry_context)
        employee_info["employee_id"] = employee_id
        employee_info["security_level"] = sec_level.value
        
        return jsonify({
            'employee': employee_info,
            'security_level': security_level,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/employees/search', methods=['POST'])
@require_api_key
def search_employees():
    """Search employees with security level filtering"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        security_level = data.get('security_level', 'public')
        inquiry_context = data.get('context', {})
        
        # Convert string to SecurityLevel enum
        try:
            sec_level = SecurityLevel(security_level)
        except ValueError:
            sec_level = SecurityLevel.PUBLIC
        
        employees = employee_db.search_employees(query, sec_level, inquiry_context)
        
        return jsonify({
            'employees': employees,
            'count': len(employees),
            'query': query,
            'security_level': security_level,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(f"🚀 Starting Email Assistant API Server...")
    print(f"   Port: {PORT}")
    print(f"   Debug: {DEBUG}")
    print(f"   API Key: {API_KEY[:10]}...")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
