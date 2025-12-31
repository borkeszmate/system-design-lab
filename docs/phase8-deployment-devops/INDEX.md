# Phase 8: Deployment & DevOps - Index

## Overview

**Total Content:** ~40 KB
**Estimated Reading Time:** 75-90 minutes
**Difficulty:** Intermediate to Advanced

Modern deployment practices covering containerization, Kubernetes orchestration, CI/CD pipelines, deployment strategies, and infrastructure as code.

---

## 📚 Documents

### [deployment-devops.md](./deployment-devops.md) (~40 KB)

**Complete guide to deployment and DevOps practices**

---

## 🎯 Quick Reference

### Deployment Strategies

| Strategy | Traffic Shift | Rollback | Risk | Complexity |
|----------|---------------|----------|------|------------|
| **Rolling Update** | Gradual | Medium | Low | Low |
| **Blue-Green** | Instant | Instant | Medium | Medium |
| **Canary** | Progressive | Easy | Low | High |

### Container Image Best Practices

✅ **DO:**
- Use specific tags (python:3.11-slim)
- Multi-stage builds
- Run as non-root user
- Include healthchecks
- Use .dockerignore

❌ **DON'T:**
- Use `latest` tag in production
- Include secrets in image
- Run as root
- Create unnecessary layers

---

## 🗺️ Content Map

### Section 1: Containerization with Docker (~10 KB, 20 min)
- **1.1 Docker Basics**
  - Dockerfile best practices
  - Multi-stage builds
  - Security (non-root user)

- **1.2 Docker Compose**
  - Service definitions
  - Health checks
  - Volume management

### Section 2: Kubernetes Orchestration (~15 KB, 30 min)
- **2.1 Core Concepts**
  - Deployments
  - Services
  - Ingress

- **2.2 ConfigMaps and Secrets**
  - Configuration management
  - Secret injection

- **2.3 Horizontal Pod Autoscaler**
  - CPU/Memory-based scaling
  - Custom metrics
  - Scaling policies

- **2.4 Persistent Storage**
  - PersistentVolumeClaims
  - StatefulSets

### Section 3: CI/CD Pipelines (~8 KB, 15 min)
- **3.1 GitHub Actions**
  - Test, build, deploy workflow
  - Container registry integration

- **3.2 GitLab CI**
  - Multi-stage pipelines
  - Environment-specific deployments

### Section 4: Deployment Strategies (~5 KB, 10 min)
- **4.1 Blue-Green Deployment**
  - Two identical environments
  - Instant switch

- **4.2 Canary Deployment**
  - Progressive rollout
  - Risk mitigation

- **4.3 Rolling Update**
  - Kubernetes default
  - MaxSurge/MaxUnavailable

### Section 5: Infrastructure as Code (~7 KB, 15 min)
- **5.1 Terraform**
  - AWS infrastructure
  - State management

- **5.2 Helm Charts**
  - Kubernetes package manager
  - Values and templates

---

## ✅ Learning Checklist

### Docker
- [ ] Write production-ready Dockerfile
- [ ] Implement multi-stage builds
- [ ] Optimize image size (< 200MB for Python/Node apps)
- [ ] Configure healthchecks
- [ ] Run containers as non-root
- [ ] Use Docker Compose for local development

### Kubernetes
- [ ] Understand Pods, Deployments, Services
- [ ] Deploy application to Kubernetes
- [ ] Configure resource requests and limits
- [ ] Implement liveness and readiness probes
- [ ] Use ConfigMaps for configuration
- [ ] Use Secrets for sensitive data
- [ ] Set up Horizontal Pod Autoscaler
- [ ] Configure Ingress with TLS

### CI/CD
- [ ] Set up automated testing pipeline
- [ ] Build and push Docker images automatically
- [ ] Deploy to staging on merge to develop
- [ ] Deploy to production on merge to main
- [ ] Implement smoke tests after deployment
- [ ] Add manual approval for production
- [ ] Set up rollback mechanism

### Deployment
- [ ] Understand rolling update strategy
- [ ] Implement blue-green deployment
- [ ] Implement canary deployment
- [ ] Test rollback procedure
- [ ] Monitor deployment health

### Infrastructure as Code
- [ ] Write Terraform configuration
- [ ] Create Helm chart for application
- [ ] Version control infrastructure code
- [ ] Use separate environments (dev, staging, prod)
- [ ] Implement infrastructure testing

---

## 💡 Key Concepts

### Kubernetes Resource Requests vs Limits
```yaml
resources:
  requests:    # Guaranteed resources
    memory: "256Mi"
    cpu: "250m"
  limits:      # Maximum resources
    memory: "512Mi"
    cpu: "500m"
```

### Rolling Update Strategy
```
Total: 10 pods (old version)
MaxSurge: 3 (can create 3 extra pods)
MaxUnavailable: 1 (at most 1 pod unavailable)

Process:
1. Create 3 new pods (total: 13)
2. Terminate 1 old pod (total: 12)
3. Repeat until all pods are new
```

### Blue-Green Deployment
```
Blue (v1): 100% traffic → 0% traffic
Green (v2): 0% traffic → 100% traffic

Switch is instant by changing Service selector
```

---

## 🛠️ Hands-On Exercises

### Exercise 1: Dockerize Application
**Time:** 45 minutes
**Difficulty:** Medium

Create production-ready Docker setup:
1. Write multi-stage Dockerfile
2. Create .dockerignore file
3. Build and run container locally
4. Optimize image size
5. Add healthcheck endpoint

### Exercise 2: Deploy to Kubernetes
**Time:** 90 minutes
**Difficulty:** Hard

Deploy application to Kubernetes:
1. Set up local Kubernetes (minikube/kind)
2. Create Deployment, Service, Ingress manifests
3. Configure ConfigMap and Secret
4. Set resource requests and limits
5. Add health probes
6. Deploy and verify

### Exercise 3: CI/CD Pipeline
**Time:** 60 minutes
**Difficulty:** Medium

Create automated pipeline:
1. Set up GitHub Actions or GitLab CI
2. Add test stage (linting, unit tests)
3. Add build stage (build Docker image)
4. Add deploy stage (deploy to K8s)
5. Test by pushing code change

### Exercise 4: Canary Deployment
**Time:** 45 minutes
**Difficulty:** Medium

Implement canary deployment:
1. Deploy v1 with 10 replicas
2. Deploy v2 with 1 replica (10% traffic)
3. Monitor metrics for 5 minutes
4. Gradually increase v2 to 50%
5. Complete rollout to 100% v2

---

## 📊 Tool Comparison

### CI/CD Platforms

| Tool | Best For | Pricing | Kubernetes Integration |
|------|----------|---------|------------------------|
| **GitHub Actions** | GitHub projects | Free tier generous | ✅ Excellent |
| **GitLab CI** | All-in-one DevOps | Free tier good | ✅ Excellent |
| **Jenkins** | Self-hosted | Free (self-host) | ✅ Good |
| **CircleCI** | Fast builds | Paid | ✅ Good |

### Infrastructure as Code

| Tool | Best For | Learning Curve | Multi-Cloud |
|------|----------|----------------|-------------|
| **Terraform** | General IaC | Medium | ✅ Yes |
| **Pulumi** | Familiar languages | Low | ✅ Yes |
| **CloudFormation** | AWS only | High | ❌ No |
| **Helm** | Kubernetes only | Medium | N/A |

---

## 🎓 Prerequisites

**Before starting this phase:**
- Docker basics (build, run, push)
- Basic Kubernetes concepts
- Git and GitHub/GitLab
- YAML syntax
- Shell scripting basics

**Technical setup:**
- Docker Desktop or equivalent
- Kubernetes cluster (minikube, kind, or cloud)
- kubectl CLI
- Helm CLI (optional)
- Terraform CLI (optional)

---

## 📈 Progress Tracking

### Estimated Timeline
- **Reading:** 75-90 minutes
- **Hands-on exercises:** 4-5 hours
- **Total:** 5.5-6.5 hours

### Completion Criteria
- [ ] Read all sections
- [ ] Create production Dockerfile
- [ ] Deploy app to Kubernetes
- [ ] Set up CI/CD pipeline
- [ ] Implement one deployment strategy
- [ ] (Optional) Use Terraform/Helm

---

## 🔗 Related Topics

**From Other Phases:**
- Phase 5: Health checks in deployments
- Phase 6: Monitoring deployments
- Phase 7: Secrets in Kubernetes

**Next Steps:**
- GitOps (ArgoCD, Flux)
- Service Mesh (Istio, Linkerd)
- Advanced Kubernetes (Operators, CRDs)

---

## 📝 Notes

**Token Conservation:**
Do not read this file unless the user explicitly asks about deployment, DevOps, Docker, Kubernetes, CI/CD, containers, orchestration, Terraform, Helm, or related topics.
