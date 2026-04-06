# AWS Deployment — Multi-Plan Implementation Prompt

Use this prompt with an AI coding assistant to implement the chosen AWS deployment plan.

---

## Prompt Template

```
I have DERAI — a 3-service document processing application:
- FastAPI (Python) — PDF extraction, AI classification (6 providers: OpenAI, GitHub Copilot, Anthropic Claude, Google Gemini, DeepSeek, Regex)
- Spring Boot (Java) — PDFBox extraction and comparison data
- React UI (TypeScript/Vite) — Upload dashboard with provider/model selection

Current setup: Docker Compose with 3 containers on a bridge network.
Repo: https://github.com/shrikantkingdom/CodeLab (under DERAI/ directory)

I want to deploy to AWS using [CHOOSE ONE: Plan A / Plan B / Plan C]:

## Plan A: EC2 + Docker Compose
- Launch t3.medium EC2 instance
- Install Docker, clone repo, run docker compose
- Add Nginx reverse proxy with Let's Encrypt SSL
- Set up CloudWatch agent for logs
- Use S3 for PDF storage
- Budget: ~$40/month

## Plan B: ECS Fargate (Recommended)
- Push 3 images to ECR
- Create ECS Fargate cluster with 3 services
- ALB with path-based routing (/api → FastAPI, /springboot → Spring Boot)
- React UI → S3 + CloudFront
- Secrets in AWS Secrets Manager
- Auto-scaling (2-10 tasks)
- GitHub Actions CI/CD pipeline
- Budget: ~$130/month

## Plan C: EKS (Kubernetes)
- Create EKS cluster with eksctl
- Kubernetes manifests (Deployment, Service, Ingress, HPA)
- Helm charts for each service
- AWS ALB Ingress Controller
- External Secrets Operator for AWS Secrets Manager
- GitOps with ArgoCD
- Budget: ~$200+/month

Please implement [Plan X] step by step:
1. Create all required AWS infrastructure (IaC using Terraform or CloudFormation)
2. Create Dockerfiles optimized for production (multi-stage builds)
3. Create CI/CD pipeline (GitHub Actions)
4. Configure secrets management
5. Set up monitoring and alerting
6. Configure custom domain with HTTPS
7. Add health check endpoints

Environment variables needed:
- AI_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL
- GITHUB_TOKEN, GITHUB_COPILOT_MODEL
- ANTHROPIC_API_KEY, ANTHROPIC_MODEL
- GOOGLE_API_KEY, GOOGLE_MODEL
- DEEPSEEK_API_KEY, DEEPSEEK_MODEL
- SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, etc.
- SPRINGBOOT_BASE_URL (inter-service communication)

Services communicate over internal network:
- FastAPI calls Spring Boot at http://springboot:8080
- React UI calls FastAPI at http://localhost:8000 (needs ALB URL in prod)

Generate all files needed for deployment.
```

---

## Quick Start Commands (After Implementation)

### Plan A
```bash
# SSH into EC2
ssh -i derai-key.pem ec2-user@<ec2-public-ip>
cd CodeLab/DERAI
docker compose up -d
```

### Plan B
```bash
# First-time setup
terraform init && terraform apply
# Subsequent deploys happen via GitHub Actions on push to main
```

### Plan C
```bash
eksctl create cluster -f cluster.yaml
kubectl apply -f k8s/
helm install derai ./helm/derai
```
