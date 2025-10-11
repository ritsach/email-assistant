# Email Assistant API Deployment Guide

## Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements-api.txt

# Set environment variables
export EMAIL_ASSISTANT_API_KEY="your-secret-key-here"
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"

# Run the API server
python api_server.py
```

The API will be available at `http://localhost:5000`

### 2. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f email-assistant-api
```

### 3. Cloud Deployment

#### AWS ECS/Fargate

1. **Create ECS Cluster:**
```bash
aws ecs create-cluster --cluster-name email-assistant-cluster
```

2. **Create Task Definition:**
```json
{
  "family": "email-assistant-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "email-assistant-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/email-assistant-api:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PORT",
          "value": "5000"
        }
      ],
      "secrets": [
        {
          "name": "EMAIL_ASSISTANT_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:email-assistant/api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/email-assistant-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create Service:**
```bash
aws ecs create-service \
  --cluster email-assistant-cluster \
  --service-name email-assistant-api \
  --task-definition email-assistant-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

#### Google Cloud Run

1. **Build and push image:**
```bash
# Build image
docker build -t gcr.io/your-project/email-assistant-api .

# Push to Google Container Registry
docker push gcr.io/your-project/email-assistant-api
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy email-assistant-api \
  --image gcr.io/your-project/email-assistant-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars EMAIL_ASSISTANT_API_KEY=your-secret-key
```

#### Azure Container Instances

1. **Create resource group:**
```bash
az group create --name email-assistant-rg --location eastus
```

2. **Deploy container:**
```bash
az container create \
  --resource-group email-assistant-rg \
  --name email-assistant-api \
  --image your-registry.azurecr.io/email-assistant-api:latest \
  --dns-name-label email-assistant-api \
  --ports 5000 \
  --environment-variables EMAIL_ASSISTANT_API_KEY=your-secret-key
```

## Production Setup

### 1. Environment Configuration

Create a `.env` file:
```bash
# Copy example
cp env.example .env

# Edit with your values
nano .env
```

Required environment variables:
```bash
EMAIL_ASSISTANT_API_KEY=your-secret-api-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1
PORT=5000
DEBUG=false
```

### 2. SSL/TLS Setup

#### Using Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /etc/nginx/ssl/key.pem
```

#### Using Cloud Provider SSL

- **AWS:** Use Application Load Balancer with ACM certificate
- **Google Cloud:** Use Cloud Load Balancing with managed SSL certificates
- **Azure:** Use Application Gateway with SSL certificates

### 3. Database Setup (Optional)

For production, consider using a database for job persistence:

#### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb email_assistant

# Create user
sudo -u postgres createuser --interactive
```

#### Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 4. Monitoring Setup

#### Prometheus + Grafana

1. **Install Prometheus:**
```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-2.40.0.linux-amd64.tar.gz
cd prometheus-2.40.0.linux-amd64

# Start Prometheus
./prometheus --config.file=prometheus.yml
```

2. **Install Grafana:**
```bash
# Add Grafana repository
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

# Install Grafana
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### Health Checks

Add health check endpoint monitoring:
```bash
# Simple health check script
#!/bin/bash
curl -f http://localhost:5000/health || exit 1
```

### 5. Backup Strategy

#### Gmail Credentials Backup
```bash
# Backup Gmail credentials
cp credentials.json credentials.json.backup
cp token.json token.json.backup

# Store in secure location
gpg --symmetric --cipher-algo AES256 credentials.json.backup
```

#### AWS Credentials Backup
```bash
# Backup AWS credentials
cp ~/.aws/credentials ~/.aws/credentials.backup
cp ~/.aws/config ~/.aws/config.backup
```

### 6. Security Hardening

#### Firewall Configuration
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5000/tcp   # Block direct API access
```

#### API Key Security
```bash
# Generate secure API key
openssl rand -hex 32

# Store in environment variable
echo 'export EMAIL_ASSISTANT_API_KEY="generated-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Rate Limiting
```bash
# Configure nginx rate limiting
sudo nano /etc/nginx/sites-available/email-assistant

# Add rate limiting rules
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

## Troubleshooting

### Common Issues

1. **API Key Authentication Failed**
   - Check environment variable: `echo $EMAIL_ASSISTANT_API_KEY`
   - Verify API key in request headers
   - Check server logs for authentication errors

2. **Gmail API Authentication Failed**
   - Verify `credentials.json` exists
   - Check `token.json` permissions
   - Re-authenticate if token expired

3. **AWS Bedrock Connection Failed**
   - Verify AWS credentials: `aws sts get-caller-identity`
   - Check AWS region configuration
   - Verify Bedrock model access

4. **High Memory Usage**
   - Monitor with `htop` or `docker stats`
   - Increase container memory limits
   - Implement job queue with Redis

5. **Slow Response Times**
   - Check database connections
   - Monitor API response times
   - Implement caching for frequent requests

### Log Analysis

```bash
# View application logs
docker-compose logs -f email-assistant-api

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View system logs
sudo journalctl -u email-assistant-api -f
```

### Performance Monitoring

```bash
# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:5000/health"

# Monitor memory usage
free -h
docker stats

# Monitor disk usage
df -h
```

## Scaling

### Horizontal Scaling

1. **Load Balancer Configuration**
```bash
# Configure nginx upstream
upstream email_assistant {
    server 10.0.1.10:5000;
    server 10.0.1.11:5000;
    server 10.0.1.12:5000;
}
```

2. **Auto-scaling Setup**
```bash
# AWS ECS Auto Scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/email-assistant-cluster/email-assistant-api \
  --min-capacity 2 \
  --max-capacity 10
```

### Vertical Scaling

1. **Increase Container Resources**
```yaml
# docker-compose.yml
services:
  email-assistant-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

2. **Database Optimization**
```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**
```bash
# Check for updates
pip list --outdated

# Update requirements
pip freeze > requirements-api.txt
```

2. **Backup Data**
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz credentials.json token.json ~/.aws/
```

3. **Monitor Logs**
```bash
# Log rotation setup
sudo nano /etc/logrotate.d/email-assistant

# Log rotation configuration
/var/log/email-assistant/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

### Updates

1. **Application Updates**
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

2. **Security Updates**
```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade

# Update Docker images
docker-compose pull
docker-compose up -d
```

## Support

For deployment issues:
1. Check the health endpoint first
2. Review error logs
3. Verify environment variables
4. Test API endpoints individually
5. Contact support with specific error messages
