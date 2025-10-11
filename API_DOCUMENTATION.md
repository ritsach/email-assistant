# Email Assistant REST API Documentation

## Overview

The Email Assistant REST API provides programmatic access to the AI-powered email processing system. It allows external applications to analyze emails, generate replies, and manage email workflows.

### Security Levels

The system implements a three-level security system for information disclosure:

- **PUBLIC**: Basic company information, general contacts, and public services
- **TRUSTED**: Additional contact details, phone numbers, and service pricing for trusted partners
- **CONFIDENTIAL**: Detailed information, internal processes, and sensitive data for verified partners

Security levels are automatically determined based on:
- Sender domain (trusted domains get higher access)
- Inquiry content (partnership/investment keywords trigger higher access)
- Urgency level (urgent requests get trusted access)

## Base URL

```
https://your-domain.com/api/v1
```

## Authentication

All API requests require authentication using an API key. Include the API key in one of the following ways:

### Header (Recommended)
```http
X-API-Key: your-secret-api-key-here
```

### Query Parameter
```http
GET /api/v1/health?api_key=your-secret-api-key-here
```

## Endpoints

### Health Check

**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Process Emails

**POST** `/api/v1/emails/process`

Process all unread emails in the Gmail inbox.

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {}
}
```

**Job Status Check:**
```http
GET /api/v1/jobs/{job_id}
```

**Completed Job Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "output": "Found 3 unread messages to process...",
    "processed_at": "2024-01-15T10:32:00Z"
  }
}
```

### Analyze Email

**POST** `/api/v1/emails/analyze`

Analyze a single email for intent and generate appropriate response.

**Request Body:**
```json
{
  "email": {
    "sender": "john.doe@example.com",
    "subject": "Question about your services",
    "body": "Hi, I'm interested in learning more about your AI consulting services. Can you send me more information?"
  }
}
```

**Response:**
```json
{
  "analysis": {
    "intent": {
      "primary_intent": "sales_inquiry",
      "urgency": "normal",
      "category": "sales",
      "requires_reply": true,
      "requires_forwarding": true,
      "disclosure_level": "standard"
    },
    "response_info": {
      "disclosure_level": "standard",
      "company_info": {
        "name": "TechCorp Solutions",
        "website": "https://techcorp.com"
      },
      "contacts": [
        {
          "type": "sales",
          "info": {
            "name": "David Rodriguez",
            "email": "david.rodriguez@techcorp.com",
            "title": "VP of Sales"
          }
        }
      ]
    }
  },
  "should_reply": true,
  "reply_text": "Hi John,\n\nThank you for your interest in our AI consulting services! I'd be happy to provide you with more information...",
  "forward_to": "david.rodriguez@techcorp.com",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Send Email

**POST** `/api/v1/emails/send`

Send an email through the Gmail API.

**Request Body:**
```json
{
  "to": "recipient@example.com",
  "subject": "Re: Question about your services",
  "body": "Thank you for your inquiry. Here's the information you requested..."
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "1234567890abcdef",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Search Knowledge Base

**POST** `/api/v1/knowledge/search`

Search the company knowledge base for contacts and information.

**Request Body:**
```json
{
  "query": "sales manager",
  "context": {
    "sender": "john.doe@example.com",
    "subject": "Sales inquiry",
    "body": "I need to speak with your sales manager"
  }
}
```

**Response:**
```json
{
  "contacts": [
    {
      "category": "management",
      "role": "vp_sales",
      "info": {
        "name": "David Rodriguez",
        "email": "david.rodriguez@techcorp.com",
        "title": "VP of Sales",
        "phone": "+1 (555) 200-0001"
      }
    }
  ],
  "response_info": {
    "disclosure_level": "standard",
    "company_info": {
      "name": "TechCorp Solutions",
      "website": "https://techcorp.com"
    },
    "contacts": [
      {
        "type": "sales",
        "info": {
          "name": "David Rodriguez",
          "email": "david.rodriguez@techcorp.com",
          "title": "VP of Sales"
        }
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Job Management

**GET** `/api/v1/jobs`

List all jobs.

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "timestamp": "2024-01-15T10:30:00Z",
      "data": {
        "output": "Processed 3 emails successfully"
      }
    }
  ],
  "count": 1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**GET** `/api/v1/jobs/{job_id}`

Get status of a specific job.

### Employee Management

**GET** `/api/v1/employees`

List employees with security level filtering.

**Query Parameters:**
- `security_level` (optional): `public`, `trusted`, or `confidential` (default: `public`)
- `department` (optional): Filter by department name

**Response:**
```json
{
  "employees": [
    {
      "name": "Sarah Johnson",
      "title": "Chief Executive Officer",
      "company_email": "sarah.johnson@techcorp.com",
      "department": "Executive",
      "security_level": "public",
      "employee_id": "EMP001"
    }
  ],
  "count": 1,
  "security_level": "public",
  "department": "",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**GET** `/api/v1/employees/{employee_id}`

Get specific employee information.

**Query Parameters:**
- `security_level` (optional): `public`, `trusted`, or `confidential` (default: `public`)

**Response:**
```json
{
  "employee": {
    "name": "Sarah Johnson",
    "title": "Chief Executive Officer",
    "company_email": "sarah.johnson@techcorp.com",
    "department": "Executive",
    "security_level": "public",
    "employee_id": "EMP001"
  },
  "security_level": "public",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**POST** `/api/v1/employees/search`

Search employees with security level filtering.

**Request Body:**
```json
{
  "query": "CEO",
  "security_level": "trusted",
  "context": {
    "sender": "partner@berkeley.edu",
    "subject": "Partnership discussion",
    "body": "We want to discuss a strategic partnership"
  }
}
```

**Response:**
```json
{
  "employees": [
    {
      "name": "Sarah Johnson",
      "title": "Chief Executive Officer",
      "company_email": "sarah.johnson@techcorp.com",
      "phone": "+1 (555) 100-0001",
      "department": "Executive",
      "security_level": "trusted",
      "employee_id": "EMP001"
    }
  ],
  "count": 1,
  "query": "CEO",
  "security_level": "trusted",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Configuration

**GET** `/api/v1/config`

Get current configuration.

**Response:**
```json
{
  "contacts": {
    "sales": "ads.al@laposte.net",
    "support": "victor.sana@berkeley.edu",
    "technical": "idris.houiralami@berkeley.edu"
  },
  "aws_region": "us-east-1",
  "bedrock_model": "anthropic.claude-sonnet-4-5-20250929-v1:0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**PUT** `/api/v1/config`

Update configuration (demo only - not persisted).

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request (missing or invalid parameters)
- `401` - Unauthorized (invalid or missing API key)
- `404` - Not Found (endpoint or resource not found)
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting:
- **10 requests per second** per IP address
- **Burst limit**: 20 requests
- Rate limit headers are included in responses

## Examples

### Python Client Example

```python
import requests
import json

# Configuration
API_BASE_URL = "https://your-domain.com/api/v1"
API_KEY = "your-secret-api-key-here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Analyze an email
email_data = {
    "email": {
        "sender": "customer@example.com",
        "subject": "Need help with my account",
        "body": "I'm having trouble logging into my account. Can you help?"
    }
}

response = requests.post(
    f"{API_BASE_URL}/emails/analyze",
    headers=headers,
    json=email_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Should reply: {result['should_reply']}")
    print(f"Reply text: {result['reply_text']}")
    print(f"Forward to: {result['forward_to']}")
else:
    print(f"Error: {response.json()['error']}")
```

### JavaScript Client Example

```javascript
const API_BASE_URL = 'https://your-domain.com/api/v1';
const API_KEY = 'your-secret-api-key-here';

const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
};

// Process emails
async function processEmails() {
    try {
        const response = await fetch(`${API_BASE_URL}/emails/process`, {
            method: 'POST',
            headers: headers
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log('Job started:', result.job_id);
            // Poll for job completion
            pollJobStatus(result.job_id);
        } else {
            console.error('Error:', result.error);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

// Poll job status
async function pollJobStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
        headers: headers
    });
    
    const job = await response.json();
    
    if (job.status === 'completed') {
        console.log('Job completed:', job.data);
    } else if (job.status === 'failed') {
        console.error('Job failed:', job.data.error);
    } else {
        // Still processing, check again in 5 seconds
        setTimeout(() => pollJobStatus(jobId), 5000);
    }
}
```

### cURL Examples

```bash
# Health check
curl -H "X-API-Key: your-secret-api-key-here" \
     https://your-domain.com/health

# Analyze email
curl -X POST \
     -H "X-API-Key: your-secret-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{
       "email": {
         "sender": "customer@example.com",
         "subject": "Need help",
         "body": "I need assistance with my account"
       }
     }' \
     https://your-domain.com/api/v1/emails/analyze

# Process emails
curl -X POST \
     -H "X-API-Key: your-secret-api-key-here" \
     https://your-domain.com/api/v1/emails/process

# Check job status
curl -H "X-API-Key: your-secret-api-key-here" \
     https://your-domain.com/api/v1/jobs/job-id-here
```

## Deployment

### Docker Deployment

1. **Build the image:**
```bash
docker build -t email-assistant-api .
```

2. **Run with Docker Compose:**
```bash
docker-compose up -d
```

3. **Set environment variables:**
```bash
export EMAIL_ASSISTANT_API_KEY="your-secret-key"
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
```

### Cloud Deployment

#### AWS ECS/Fargate
- Use the provided Dockerfile
- Set up Application Load Balancer
- Configure auto-scaling
- Use AWS Secrets Manager for API keys

#### Google Cloud Run
- Deploy containerized application
- Set up Cloud Load Balancing
- Use Secret Manager for credentials

#### Azure Container Instances
- Deploy containerized application
- Set up Application Gateway
- Use Key Vault for secrets

### Production Considerations

1. **Security:**
   - Use HTTPS/TLS
   - Implement proper API key rotation
   - Set up rate limiting
   - Use environment variables for secrets

2. **Monitoring:**
   - Set up health checks
   - Monitor API performance
   - Log all requests
   - Set up alerts

3. **Scalability:**
   - Use load balancers
   - Implement horizontal scaling
   - Use Redis for job queue
   - Consider database for persistence

4. **Backup:**
   - Backup Gmail credentials
   - Backup AWS credentials
   - Backup configuration

## Support

For issues and questions:
- Check the health endpoint first
- Review error messages in responses
- Check server logs
- Contact support with job IDs for failed operations
