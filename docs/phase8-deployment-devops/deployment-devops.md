# Phase 8: Deployment & DevOps

## Overview

Modern deployment practices enable teams to ship code safely, frequently, and reliably. This phase covers containerization, orchestration, CI/CD pipelines, and infrastructure as code.

**Key Goal:** Automate everything from code commit to production deployment.

---

## Table of Contents

1. [Containerization with Docker](#1-containerization-with-docker)
2. [Kubernetes Orchestration](#2-kubernetes-orchestration)
3. [CI/CD Pipelines](#3-cicd-pipelines)
4. [Deployment Strategies](#4-deployment-strategies)
5. [Infrastructure as Code](#5-infrastructure-as-code)

---

## 1. Containerization with Docker

### 1.1 Docker Basics

**Dockerfile:**

```dockerfile
# Multi-stage build for smaller images
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python healthcheck.py || exit 1

# Run application
CMD ["python", "main.py"]
```

**Best Practices:**

```dockerfile
# ✅ DO: Use specific tags
FROM python:3.11-slim
# ❌ DON'T: Use latest tag
FROM python:latest

# ✅ DO: Multi-stage builds
FROM node:18 as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
COPY --from=builder /app/dist /app/dist
CMD ["node", "dist/server.js"]

# ✅ DO: Minimize layers
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ❌ DON'T: Create unnecessary layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# ✅ DO: Use .dockerignore
# .dockerignore file:
.git
.env
__pycache__
*.pyc
node_modules
.vscode
```

---

### 1.2 Docker Compose

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

---

## 2. Kubernetes Orchestration

### 2.1 Core Concepts

**Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
        version: v1
    spec:
      containers:
      - name: api
        image: myapp/api:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        startupProbe:
          httpGet:
            path: /health/startup
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30

  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

**Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

**Ingress:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
```

---

### 2.2 ConfigMaps and Secrets

**ConfigMap:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_NAME: "My Application"
  LOG_LEVEL: "info"
  FEATURE_FLAG_NEW_UI: "true"
  config.json: |
    {
      "api": {
        "timeout": 30,
        "retries": 3
      }
    }
```

**Secret:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:pass@db:5432/myapp"
  api-key: "sk_live_1234567890"
  jwt-secret: "super-secret-key"
```

**Usage in Pod:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    # From ConfigMap
    - name: APP_NAME
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: APP_NAME
    # From Secret
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-url
    # Mount ConfigMap as volume
    volumeMounts:
    - name: config
      mountPath: /etc/config
      readOnly: true
  volumes:
  - name: config
    configMap:
      name: app-config
```

---

### 2.3 Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # Custom metric scaling (requests per second)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

---

### 2.4 Persistent Storage

**PersistentVolumeClaim:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

---

## 3. CI/CD Pipelines

### 3.1 GitHub Actions

**.github/workflows/ci.yml:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: |
          flake8 . --max-line-length=120
          black --check .

      - name: Type check
        run: mypy .

      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}

      - name: Build and push image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure Kubernetes
        run: |
          echo "${{ secrets.KUBECONFIG }}" > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/api \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:main-${{ github.sha }}
          kubectl rollout status deployment/api --timeout=5m

      - name: Run smoke tests
        run: |
          # Wait for deployment
          sleep 30
          # Test critical endpoints
          curl -f https://api.example.com/health || exit 1
```

---

### 3.2 GitLab CI

**.gitlab-ci.yml:**

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  DOCKER_LATEST: $CI_REGISTRY_IMAGE:latest

# Test stage
test:
  stage: test
  image: python:3.11
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
  script:
    - flake8 .
    - pytest --cov=. --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

# Build stage
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE -t $DOCKER_LATEST .
    - docker push $DOCKER_IMAGE
    - docker push $DOCKER_LATEST
  only:
    - main
    - develop

# Deploy to staging
deploy:staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context staging
    - kubectl set image deployment/api api=$DOCKER_IMAGE
    - kubectl rollout status deployment/api
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

# Deploy to production
deploy:production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context production
    - kubectl set image deployment/api api=$DOCKER_IMAGE
    - kubectl rollout status deployment/api
  environment:
    name: production
    url: https://api.example.com
  when: manual  # Require manual approval
  only:
    - main
```

---

## 4. Deployment Strategies

### 4.1 Blue-Green Deployment

```yaml
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-blue
  labels:
    app: api
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
      version: blue
  template:
    metadata:
      labels:
        app: api
        version: blue
    spec:
      containers:
      - name: api
        image: myapp/api:v1.0.0

---
# Green deployment (new)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-green
  labels:
    app: api
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
      version: green
  template:
    metadata:
      labels:
        app: api
        version: green
    spec:
      containers:
      - name: api
        image: myapp/api:v2.0.0

---
# Service (switch between blue and green)
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
    version: blue  # Change to 'green' to switch traffic
  ports:
  - port: 80
    targetPort: 8000
```

**Switch script:**

```bash
#!/bin/bash
# Switch from blue to green

# Deploy green
kubectl apply -f api-green.yaml

# Wait for green to be ready
kubectl rollout status deployment/api-green

# Run smoke tests on green
curl -f http://api-green-internal/health || exit 1

# Switch service to green
kubectl patch service api -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor for issues
sleep 300

# If all good, scale down blue
kubectl scale deployment/api-blue --replicas=0
```

---

### 4.2 Canary Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-v1
spec:
  replicas: 9  # 90% traffic
  selector:
    matchLabels:
      app: api
      version: v1
  template:
    metadata:
      labels:
        app: api
        version: v1
    spec:
      containers:
      - name: api
        image: myapp/api:v1.0.0

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-v2-canary
spec:
  replicas: 1  # 10% traffic
  selector:
    matchLabels:
      app: api
      version: v2
  template:
    metadata:
      labels:
        app: api
        version: v2
    spec:
      containers:
      - name: api
        image: myapp/api:v2.0.0

---
# Service routes to both versions
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api  # Matches both v1 and v2
  ports:
  - port: 80
    targetPort: 8000
```

**Progressive rollout:**

```bash
# 1. Start with 10% canary (1 replica)
kubectl scale deployment/api-v2-canary --replicas=1

# 2. Monitor metrics for 15 minutes
# Check error rate, latency, etc.

# 3. If healthy, increase to 25% (3 replicas)
kubectl scale deployment/api-v1 --replicas=7
kubectl scale deployment/api-v2-canary --replicas=3

# 4. Monitor for 15 minutes

# 5. If healthy, increase to 50%
kubectl scale deployment/api-v1 --replicas=5
kubectl scale deployment/api-v2-canary --replicas=5

# 6. If healthy, complete rollout
kubectl scale deployment/api-v1 --replicas=0
kubectl scale deployment/api-v2-canary --replicas=10
kubectl delete deployment api-v1
```

---

### 4.3 Rolling Update (Default)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 3        # Can create 3 extra pods during update
      maxUnavailable: 1  # At most 1 pod can be unavailable
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: myapp/api:v2.0.0

# Rolling update process:
# 1. Create 3 new pods with v2
# 2. Wait for them to be ready
# 3. Terminate 1 old pod
# 4. Create 1 new pod
# 5. Repeat until all pods are v2
```

---

## 5. Infrastructure as Code

### 5.1 Terraform

**main.tf:**

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "main-vpc"
    Environment = var.environment
  }
}

# Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "public-subnet-${count.index + 1}"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "main-cluster"
  role_arn = aws_iam_role.cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids = aws_subnet.public[*].id
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy
  ]
}

# Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "main-node-group"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = aws_subnet.public[*].id

  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 2
  }

  instance_types = ["t3.medium"]

  depends_on = [
    aws_iam_role_policy_attachment.node_policy
  ]
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier        = "main-db"
  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "myapp"
  username = "admin"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  skip_final_snapshot     = false
  final_snapshot_identifier = "main-db-final-snapshot"

  tags = {
    Environment = var.environment
  }
}
```

**variables.tf:**

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

**Commands:**

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan -var-file="production.tfvars"

# Apply changes
terraform apply -var-file="production.tfvars"

# Destroy infrastructure
terraform destroy -var-file="production.tfvars"
```

---

### 5.2 Helm Charts

**Chart.yaml:**

```yaml
apiVersion: v2
name: myapp
description: My Application Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"
```

**values.yaml:**

```yaml
replicaCount: 3

image:
  repository: myapp/api
  tag: "1.0.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.example.com

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

env:
  - name: LOG_LEVEL
    value: "info"
```

**templates/deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: 8000
        env:
        {{- toYaml .Values.env | nindent 8 }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

**Commands:**

```bash
# Install chart
helm install myapp ./myapp

# Upgrade chart
helm upgrade myapp ./myapp

# Install/upgrade
helm upgrade --install myapp ./myapp

# With custom values
helm install myapp ./myapp -f values-production.yaml

# Dry run
helm install myapp ./myapp --dry-run --debug

# Rollback
helm rollback myapp 1
```

---

## Summary and Key Takeaways

### Containerization
- Use multi-stage builds for smaller images
- Never use `latest` tag in production
- Run containers as non-root user
- Use .dockerignore to reduce image size

### Kubernetes
- Use resource requests and limits
- Implement health checks (liveness, readiness, startup)
- Use HPA for autoscaling
- Separate config from code (ConfigMaps, Secrets)

### CI/CD
- Automate testing and deployment
- Use different pipelines for different environments
- Implement smoke tests after deployment
- Require manual approval for production

### Deployment Strategies
- **Rolling update:** Gradual, low risk
- **Blue-green:** Instant switch, easy rollback
- **Canary:** Progressive validation

### Infrastructure as Code
- Version control infrastructure
- Use Terraform for cloud resources
- Use Helm for Kubernetes applications
- Always review changes before applying

---

## Additional Resources

### Tools
- **Container:** Docker, Podman
- **Orchestration:** Kubernetes, Docker Swarm
- **CI/CD:** GitHub Actions, GitLab CI, Jenkins, CircleCI
- **IaC:** Terraform, Pulumi, CloudFormation
- **Package Manager:** Helm, Kustomize

### Books
- "Kubernetes in Action"
- "Continuous Delivery" by Jez Humble
- "Terraform: Up & Running"
