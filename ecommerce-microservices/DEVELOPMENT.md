# Local Development Guide

This guide covers developing with Docker containers while maintaining proper VS Code IntelliSense and dependency resolution.

## Quick Setup

### 1. Install Prerequisites
```bash
# Python and Poetry (for IDE support only)
brew install python@3.11 poetry

# Node.js (for frontend IDE support)
brew install node
```

### 2. Install Dependencies Locally (For VS Code Only)
```bash
cd ecommerce-microservices

# Install Python dependencies for each service (for IntelliSense)
cd api-gateway && poetry install && cd ..
for service in services/*; do
  cd "$service" && poetry install && cd ../..
done

# Install frontend dependencies (for IntelliSense)
cd frontend && npm install && cd ..
```

**Why?** These create `.venv` folders that VS Code uses for autocomplete, import resolution, and error checking. You won't run these locally.

### 3. Open the Workspace
```bash
code microservices.code-workspace
```

This workspace file tells VS Code to use each service's `.venv` for IntelliSense.

### 4. Run Everything in Docker
```bash
docker compose up --build
```

That's it! Edit code in VS Code, run in Docker.

---

## VS Code Workspace Explained

The `microservices.code-workspace` file makes each service appear as a separate folder with its own Python interpreter:

```
🌐 Root
🚪 API Gateway          → uses api-gateway/.venv
🛍️ Product Service     → uses services/product-service/.venv
👤 User Service        → uses services/user-service/.venv
...
```

**Benefits:**
- ✅ Full IntelliSense and autocomplete
- ✅ Import resolution works correctly
- ✅ Type checking and linting
- ✅ Each service isolated

**Note:** You're NOT running services locally. Docker handles that. The `.venv` is purely for IDE features.

---

## Adding a New Microservice

### 1. Create and Set Up Service
```bash
cd services
mkdir inventory-service
cd inventory-service

# Copy structure from existing service
cp -r ../product-service/{pyproject.toml,Dockerfile,app} .

# Edit pyproject.toml (change name)
# Edit app/main.py (change service logic)

# Install dependencies (for VS Code)
poetry install
```

### 2. Update Workspace File

Edit `microservices.code-workspace`:
```json
{
  "name": "📦 Inventory Service",
  "path": "services/inventory-service",
  "settings": {
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
  }
}
```

Add this to the `"folders"` array.

### 3. Update Docker Compose
Add your service to `docker-compose.yml`:
```yaml
inventory-service:
  build: ./services/inventory-service
  ports:
    - "8006:8006"
  depends_on:
    - rabbitmq
```

### 4. Reload
```bash
# Close and reopen workspace
code microservices.code-workspace

# Start with Docker
docker compose up --build
```

---

## Common Tasks

### Adding a Python Dependency
```bash
cd services/product-service
poetry add requests          # Add dependency
poetry install               # Install locally for VS Code
docker compose up --build    # Rebuild container
```

### Viewing Logs
```bash
docker compose logs -f product-service
```

### Database Access
```bash
# Order Service DB
docker exec -it microservices-order-db psql -U order_user -d order_db

# Payment Service DB
docker exec -it microservices-payment-db psql -U payment_user -d payment_db
```

### Running Tests
```bash
# Inside container
docker compose exec product-service pytest

# Or locally (if you want faster iteration)
cd services/product-service
poetry run pytest
```

---

## Troubleshooting

### VS Code Shows Import Errors

**Problem:** Red squiggles on imports, even though code runs in Docker

**Fix:**
1. Check Python interpreter (bottom-right status bar)
2. Should show `.venv/bin/python` for the current service
3. If not: Click it → Select Interpreter → Choose `.venv/bin/python`
4. If still broken: `poetry install` in the service folder

### New Service Not in Workspace

**Problem:** Added service but it's not in VS Code sidebar

**Fix:**
1. Verify you added it to `microservices.code-workspace`
2. Close and reopen: `code microservices.code-workspace`
3. Check the `"path"` is correct

### Poetry Install Fails

**Problem:** Dependency conflicts or errors

**Fix:**
```bash
rm poetry.lock
poetry lock
poetry install
```

---

## Summary

**Development Workflow:**
1. Edit code in VS Code (with full IntelliSense)
2. Docker auto-reloads on file changes
3. View logs with `docker compose logs -f`
4. Test with `docker compose exec <service> pytest`

**The workspace is just for IDE support. Everything runs in Docker.**

For production deployment details, see [README.md](./README.md).
