# AWS Cloud Deployment — DERAI

## Overview

This document covers the strategy for deploying the DERAI 3-service stack
(FastAPI, Spring Boot, React UI) to AWS. Multiple deployment plans are provided
ranging from quick/simple to production-grade.

---

## Architecture on AWS

```
                         ┌──────────────────┐
                         │   Route 53 (DNS) │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │  CloudFront CDN   │
                         │  (React UI static)│
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │              │
           ┌────────▼──┐  ┌──────▼────┐  ┌─────▼──────┐
           │  S3 Bucket │  │    ALB    │  │    ALB     │
           │  (React)   │  │ (:8000)   │  │  (:8080)   │
           └────────────┘  └────┬──────┘  └─────┬──────┘
                               │               │
                          ┌────▼──────┐   ┌────▼──────┐
                          │   ECS     │   │   ECS     │
                          │  FastAPI  │   │ SpringBoot│
                          │  Fargate  │   │  Fargate  │
                          └────┬──────┘   └───────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
              ┌─────▼───┐ ┌───▼────┐ ┌───▼──────┐
              │ Secrets  │ │  S3    │ │ Snowflake│
              │ Manager  │ │(PDFs)  │ │  (DB)    │
              └──────────┘ └────────┘ └──────────┘
```

---

## Plan A: Quick Deploy (EC2 + Docker Compose)

**Best for**: Dev/staging, demos, single-instance deployment  
**Cost**: ~$30-50/month (t3.medium)  
**Complexity**: Low

### Steps

1. **Launch EC2 instance**
   - AMI: Amazon Linux 2023 or Ubuntu 22.04
   - Instance type: `t3.medium` (2 vCPU, 4 GB RAM)
   - Security group: ports 80, 443, 22
   - Storage: 30 GB gp3

2. **Install Docker & Docker Compose**
   ```bash
   sudo yum install -y docker
   sudo systemctl start docker && sudo systemctl enable docker
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
     -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Clone repo & deploy**
   ```bash
   git clone https://github.com/shrikantkingdom/CodeLab.git
   cd CodeLab/DERAI
   cp .env.example .env
   # Edit .env with your API keys
   docker compose up -d
   ```

4. **Add Nginx reverse proxy** (optional, for HTTPS)
   ```bash
   sudo yum install -y nginx certbot python3-certbot-nginx
   # Configure nginx to proxy :80 → :3000, /api → :8000
   ```

### Pros/Cons
- ✅ Identical to local setup, minimal changes
- ✅ Fast to deploy (< 30 min)
- ❌ No auto-scaling, single point of failure
- ❌ Manual updates

---

## Plan B: ECS Fargate (Recommended for Production)

**Best for**: Production, auto-scaling, zero-server management  
**Cost**: ~$80-150/month depending on traffic  
**Complexity**: Medium

### Steps

1. **Push images to ECR**
   ```bash
   aws ecr create-repository --repository-name derai-fastapi
   aws ecr create-repository --repository-name derai-springboot
   aws ecr create-repository --repository-name derai-react-ui

   # Authenticate Docker to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build & push
   docker compose build
   docker tag derai-fastapi:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/derai-fastapi:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/derai-fastapi:latest
   # Repeat for springboot and react-ui
   ```

2. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name derai-cluster --capacity-providers FARGATE
   ```

3. **Store secrets in AWS Secrets Manager**
   ```bash
   aws secretsmanager create-secret --name derai/api-keys \
     --secret-string '{
       "OPENAI_API_KEY": "sk-...",
       "GITHUB_TOKEN": "ghp_...",
       "ANTHROPIC_API_KEY": "sk-ant-...",
       "GOOGLE_API_KEY": "...",
       "DEEPSEEK_API_KEY": "..."
     }'
   ```

4. **Create Task Definitions** for each service (FastAPI, Spring Boot, React UI)
   - CPU: 512, Memory: 1024 for each
   - Reference secrets from Secrets Manager
   - Configure health checks

5. **Create Application Load Balancer**
   - Target groups for FastAPI (:8000) and Spring Boot (:8080)
   - Path-based routing: `/api/*` → FastAPI, `/springboot/*` → Spring Boot

6. **Create ECS Services**
   - Desired count: 2 (for HA)
   - Auto-scaling: 2-10 tasks based on CPU utilization

7. **Deploy React UI to S3 + CloudFront**
   ```bash
   cd "React UI"
   npm run build
   aws s3 sync dist/ s3://derai-frontend/ --delete
   # Create CloudFront distribution pointing to S3
   ```

### Pros/Cons
- ✅ Auto-scaling, high availability
- ✅ No servers to manage
- ✅ Secrets managed securely
- ❌ More setup complexity
- ❌ Higher base cost

---

## Plan C: EKS (Kubernetes) — Enterprise Scale

**Best for**: Large-scale enterprise, multi-team, complex orchestration  
**Cost**: ~$200-500+/month  
**Complexity**: High

### Steps

1. Create EKS cluster with `eksctl`
2. Create Kubernetes manifests (Deployment, Service, Ingress) for each service
3. Use Helm charts for standardized deployments
4. Configure HPA (Horizontal Pod Autoscaler)
5. Use AWS ALB Ingress Controller
6. Store secrets in AWS Secrets Manager with External Secrets Operator

### When to choose this
- Multiple environments (dev, staging, prod) with GitOps
- Team already using Kubernetes
- Need fine-grained resource management

---

## Shared AWS Services (All Plans)

### S3 — PDF Storage
```bash
aws s3 mb s3://derai-documents-prod
# Configure lifecycle: move to Glacier after 90 days
```

### CloudWatch — Logging & Monitoring
- FastAPI and Spring Boot logs stream to CloudWatch Log Groups
- Set up alarms for error rates, latency

### IAM Roles
- ECS Task Role: S3 read/write, Secrets Manager read, CloudWatch Logs write
- Minimal permissions (least privilege)

### RDS / Snowflake
- For production, connect to Snowflake via private endpoint or VPC peering
- Alternative: RDS PostgreSQL for metadata storage

---

## CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2
      
      - name: Build & Push FastAPI
        run: |
          docker build -t derai-fastapi "DERAI/FastAPI services"
          docker tag derai-fastapi:latest ${{ secrets.ECR_REGISTRY }}/derai-fastapi:latest
          docker push ${{ secrets.ECR_REGISTRY }}/derai-fastapi:latest
      
      - name: Update ECS Service
        run: |
          aws ecs update-service --cluster derai-cluster \
            --service derai-fastapi --force-new-deployment
```

---

## Cost Estimation

| Component | Plan A (EC2) | Plan B (ECS Fargate) | Plan C (EKS) |
|-----------|-------------|---------------------|--------------|
| Compute | $30 (t3.medium) | $80 (3 Fargate tasks) | $150 (EKS + nodes) |
| ALB | — | $20 | $20 |
| S3 | $5 | $5 | $5 |
| CloudFront | — | $10 | $10 |
| Secrets Manager | — | $2 | $2 |
| CloudWatch | $5 | $10 | $15 |
| **Total/month** | **~$40** | **~$127** | **~$202** |

---

## Security Checklist

- [ ] API keys in AWS Secrets Manager (never in code/env files)
- [ ] HTTPS via ACM certificate + ALB/CloudFront
- [ ] VPC with private subnets for backend services
- [ ] Security groups: only ALB can reach ECS tasks
- [ ] IAM roles with least privilege
- [ ] Enable CloudTrail for audit logging
- [ ] Enable WAF on ALB/CloudFront
- [ ] Regular rotation of API keys and tokens
