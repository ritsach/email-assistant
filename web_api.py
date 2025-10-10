#!/usr/bin/env python3
"""
Web API for Email Assistant
This creates a REST API that Gemini can interact with
"""

from flask import Flask, request, jsonify
import os
import json
from email_assistant import process_emails, get_gmail_service
from ai_assistant import ai_assistant

app = Flask(__name__)

# Initialize AI assistant
ai_assistant.initialize_gemini(os.environ.get("GEMINI_API_KEY"))

@app.route('/api/process-emails', methods=['POST'])
def process_emails_endpoint():
    """Process all unread emails"""
    try:
        process_emails()
        return jsonify({"status": "success", "message": "Emails processed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analyze-email', methods=['POST'])
def analyze_email_endpoint():
    """Analyze a specific email"""
    try:
        data = request.get_json()
        sender = data.get('sender', '')
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        intent_analysis = ai_assistant.analyze_email_intent(sender, subject, body)
        return jsonify({"status": "success", "analysis": intent_analysis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate-reply', methods=['POST'])
def generate_reply_endpoint():
    """Generate a reply for an email"""
    try:
        data = request.get_json()
        sender = data.get('sender', '')
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        reply = ai_assistant.generate_intelligent_reply(sender, subject, body)
        return jsonify({"status": "success", "reply": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "email-assistant"})

@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    """Get available capabilities"""
    return jsonify({
        "capabilities": [
            "process_emails",
            "analyze_email", 
            "generate_reply"
        ],
        "endpoints": [
            "POST /api/process-emails",
            "POST /api/analyze-email",
            "POST /api/generate-reply",
            "GET /api/health",
            "GET /api/capabilities"
        ]
    })

if __name__ == '__main__':
    print("🌐 Starting Email Assistant Web API...")
    print("📡 API will be available at: http://localhost:5001")
    print("📋 Available endpoints:")
    print("   POST /api/process-emails")
    print("   POST /api/analyze-email")
    print("   POST /api/generate-reply")
    print("   GET /api/health")
    print("   GET /api/capabilities")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
