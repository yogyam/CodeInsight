# Deployment Guide

This guide covers deploying the PR Review Bot to various platforms.

## Table of Contents

- [Deploy to Render](#deploy-to-render)
- [Deploy to AWS](#deploy-to-aws)
- [Deploy to Google Cloud](#deploy-to-google-cloud)
- [Deploy to Azure](#deploy-to-azure)
- [Self-Hosted Deployment](#self-hosted-deployment)

---

## Deploy to Render

Render provides the easiest deployment with automatic setup from `render.yaml`.

### Prerequisites

- Render account
- GitHub repository
- Supabase or Render PostgreSQL database
- Environment variables ready

### Steps

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml`

2. **Configure Environment Variables**
   
   In Render dashboard, add these secret variables:
   - `GITHUB_APP_ID`
   - `ANTHROPIC_API_KEY`
   - `API_SECRET_KEY`

3. **Upload Private Key**
   - Go to your web service settings
   - Navigate to "Secret Files"
   - Upload `github-app-private-key.pem`
   - Path: `/app/github-app-private-key.pem`

4. **Deploy**
   - Click "Apply" to create all services
   - Wait for deployment to complete
   - Note your service URL (e.g., `https://your-app.onrender.com`)

5. **Update GitHub Repository Secrets**
   - Go to your repository Settings → Secrets → Actions
   - Update `REVIEW_API_URL` to: `https://your-app.onrender.com`
   - Ensure `REVIEW_API_TOKEN` matches your `API_SECRET_KEY`

### Database Setup on Render

If using Render PostgreSQL:

```sql
-- Connect to your database and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

Then run the init script:
```bash
psql $DATABASE_URL < init.sql
```

---

## Deploy to AWS

### Using AWS ECS with Fargate

#### Prerequisites

- AWS Account
- AWS CLI configured
- ECR repository created
- RDS PostgreSQL instance
- ElastiCache Redis instance

#### Steps

1. **Build and Push Docker Image**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t pr-review-bot .

# Tag image
docker tag pr-review-bot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/pr-review-bot:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/pr-review-bot:latest
```

2. **Create ECS Task Definition**

```json
{
  "family": "pr-review-bot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/pr-review-bot:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "secrets": [
        {"name": "GITHUB_APP_ID", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

3. **Create ECS Service**

```bash
aws ecs create-service \
  --cluster pr-review-bot-cluster \
  --service-name pr-review-bot-api \
  --task-definition pr-review-bot \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

4. **Set up Application Load Balancer**
   - Create ALB in AWS Console
   - Configure target group for port 8000
   - Set up health check: `/health`
   - Update GitHub repository secrets with ALB URL

---

## Deploy to Google Cloud

### Using Cloud Run

#### Prerequisites

- Google Cloud account
- gcloud CLI installed
- Cloud SQL PostgreSQL instance
- Memorystore Redis instance

#### Steps

1. **Build and Deploy**

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build with Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/pr-review-bot

# Deploy to Cloud Run
gcloud run deploy pr-review-bot \
  --image gcr.io/YOUR_PROJECT_ID/pr-review-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets GITHUB_APP_ID=github-app-id:latest,ANTHROPIC_API_KEY=anthropic-key:latest
```

2. **Connect to Cloud SQL**

```bash
gcloud run services update pr-review-bot \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:pr-bot-db \
  --set-env-vars DATABASE_URL="postgresql://user:pass@/pr_review_bot?host=/cloudsql/YOUR_PROJECT_ID:us-central1:pr-bot-db"
```

3. **Deploy Celery Worker**

```bash
gcloud run deploy pr-review-bot-worker \
  --image gcr.io/YOUR_PROJECT_ID/pr-review-bot \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --command celery,-A,app.celery_app,worker,--loglevel=info
```

---

## Deploy to Azure

### Using Azure Container Apps

#### Prerequisites

- Azure account
- Azure CLI installed
- Azure Database for PostgreSQL
- Azure Cache for Redis

#### Steps

1. **Create Container App Environment**

```bash
az containerapp env create \
  --name pr-review-bot-env \
  --resource-group pr-review-bot-rg \
  --location eastus
```

2. **Create Container App**

```bash
az containerapp create \
  --name pr-review-bot-api \
  --resource-group pr-review-bot-rg \
  --environment pr-review-bot-env \
  --image YOUR_REGISTRY/pr-review-bot:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars ENVIRONMENT=production \
  --secrets github-app-id=YOUR_APP_ID anthropic-key=YOUR_KEY
```

3. **Add Database Connection**

```bash
az containerapp update \
  --name pr-review-bot-api \
  --resource-group pr-review-bot-rg \
  --set-env-vars DATABASE_URL=secretref:database-url \
  --secrets database-url="postgresql://..."
```

---

## Self-Hosted Deployment

### Using Docker Compose in Production

#### Prerequisites

- Linux server (Ubuntu 20.04+)
- Docker and Docker Compose
- Domain name with SSL certificate

#### Steps

1. **Server Setup**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y
```

2. **Clone Repository**

```bash
git clone https://github.com/yourusername/CodeInsight.git
cd CodeInsight
```

3. **Configure Environment**

```bash
cp .env.example .env
nano .env  # Edit with your values
```

4. **Set Up SSL with Let's Encrypt**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api

  api:
    # ... existing api config
    expose:
      - "8000"
```

5. **Deploy**

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

6. **Set Up Monitoring**

```bash
# View logs
docker-compose logs -f

# Monitor resources
docker stats
```

---

## Post-Deployment Checklist

After deploying to any platform:

- [ ] Update GitHub repository secrets (REVIEW_API_URL, REVIEW_API_TOKEN)
- [ ] Test GitHub Actions workflow with a test PR
- [ ] Verify bot posts review comments
- [ ] Set up monitoring/alerting
- [ ] Configure backup for database
- [ ] Set up log aggregation
- [ ] Review and optimize resource allocation
- [ ] Document any platform-specific configurations

## Environment Variables Reference

Required variables for all platforms:

```bash
# GitHub
GITHUB_APP_ID=
GITHUB_APP_PRIVATE_KEY_PATH=

# API Security
API_SECRET_KEY=

# LLM
ANTHROPIC_API_KEY=
LLM_MODEL=claude-sonnet-4-20250514

# Database
DATABASE_URL=

# Redis
REDIS_URL=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

# Application
ENVIRONMENT=production
DEBUG=false
API_SECRET_KEY=
```

## Monitoring

Set up monitoring for:
- API health endpoint (`/health`)
- Celery worker status
- Database connections
- Redis connections
- Review task success rate
- API response times

## Scaling

To handle more reviews:
- Increase Celery workers: `--concurrency=4`
- Scale API instances horizontally
- Upgrade database plan
- Implement Redis caching
- Use CDN for static assets

## Troubleshooting

### Common Issues

1. **API request timeouts**: Increase timeout in platform settings
2. **Database connection pool exhausted**: Increase pool size in DATABASE_URL
3. **Redis memory issues**: Configure eviction policy
4. **High API latency**: Scale horizontally or increase resources
5. **GitHub Actions failing**: Check repository secrets are set correctly

For platform-specific issues, check the logs:
- Render: Dashboard → Logs
- AWS: CloudWatch
- GCP: Cloud Logging
- Azure: Application Insights
