# Docker Container vs Volume Lifecycle

## Scenario 1: Container Destroyed, Volume Preserved ✅

```bash
# Your data is SAFE in these scenarios:

# Stop and remove containers (data survives!)
docker compose down

# Restart containers (data is still there!)
docker compose up -d

# Remove just the container
docker rm -f microservices-order-db

# Recreate container
docker compose up -d order-db
```

**Result:** Your PostgreSQL data PERSISTS! All orders, payments still exist.

---

## Scenario 2: Volume Destroyed ❌

```bash
# WARNING: This DELETES your data!
docker compose down -v
# The -v flag removes volumes
```

**Result:** All database data is GONE! Fresh start.

---

## Visual Explanation

```
┌─────────────────────────────────────────────┐
│         Container (Temporary)               │
│  ┌─────────────────────────────────┐       │
│  │  PostgreSQL Process              │       │
│  │  - Runs SQL queries              │       │
│  │  - Manages connections           │       │
│  │  - Uses /var/lib/postgresql/data │       │
│  └──────────────┬──────────────────┘       │
│                 │                            │
│                 │ Mount point                │
│                 ▼                            │
└─────────────────────────────────────────────┘
                  │
                  │ Docker volume mount
                  ▼
┌─────────────────────────────────────────────┐
│     Volume (PERSISTENT Storage)             │
│                                              │
│  /var/lib/docker/volumes/                   │
│    ecommerce-microservices_order_db_data/   │
│                                              │
│  Contains:                                   │
│  - Database files (.dat, .wal, etc)         │
│  - Tables, indexes, data                    │
│  - Transaction logs                         │
│                                              │
│  ✅ Survives container deletion             │
│  ✅ Survives docker compose down            │
│  ❌ Deleted with docker compose down -v     │
└─────────────────────────────────────────────┘
```

---

## Real Example: Let's Test It!

### 1. Check current data
```bash
docker exec -it microservices-order-db psql -U order_user -d order_db -c "SELECT COUNT(*) FROM orders;"
```

### 2. Destroy container
```bash
docker compose down
# or
docker rm -f microservices-order-db
```

### 3. Restart container
```bash
docker compose up -d order-db
```

### 4. Check data again
```bash
docker exec -it microservices-order-db psql -U order_user -d order_db -c "SELECT COUNT(*) FROM orders;"
```

**Result:** Same count! Data persisted! ✅

---

## Different Volume Types

### 1. Named Volumes (What you're using) ✅
```yaml
volumes:
  - order_db_data:/var/lib/postgresql/data

volumes:
  order_db_data:  # Docker manages this
```

**Pros:**
- Docker manages storage location
- Survives container deletion
- Easy to backup with `docker volume` commands
- Portable across environments

**Cons:**
- Not directly visible in your file system (on Mac)
- Need Docker commands to access

### 2. Bind Mounts (Alternative)
```yaml
volumes:
  - ./data/postgres:/var/lib/postgresql/data
```

**Pros:**
- Data visible in your project folder
- Easy to inspect files directly
- Good for development

**Cons:**
- Path must exist
- Permission issues on Mac/Windows
- Less portable

### 3. Anonymous Volumes
```yaml
volumes:
  - /var/lib/postgresql/data  # No name
```

**Pros:**
- Quick for testing

**Cons:**
- Hard to identify
- Usually deleted with container
- Not recommended for databases

---

## Best Practices (What You're Doing) ✅

1. **Use Named Volumes for Databases**
   - Persistent
   - Managed by Docker
   - Easy to backup

2. **Separate Volume Per Database**
   ```yaml
   order_db_data:    # Order service data
   payment_db_data:  # Payment service data
   rabbitmq_data:    # RabbitMQ data
   ```

3. **Never Use -v Flag in Production**
   ```bash
   # Development: OK to reset data
   docker compose down -v
   
   # Production: NEVER! Data loss!
   docker compose down  # Keep volumes
   ```

---

## Backup Your Data

### Export database
```bash
docker exec microservices-order-db pg_dump -U order_user order_db > order_backup.sql
```

### Restore database
```bash
cat order_backup.sql | docker exec -i microservices-order-db psql -U order_user -d order_db
```

### Backup entire volume
```bash
docker run --rm \
  -v ecommerce-microservices_order_db_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/order_db_backup.tar.gz /data
```

---

## Common Commands

```bash
# List all volumes
docker volume ls

# Inspect a volume
docker volume inspect ecommerce-microservices_order_db_data

# See volume size
docker system df -v

# Remove unused volumes (CAREFUL!)
docker volume prune

# Remove specific volume (DATA LOSS!)
docker volume rm ecommerce-microservices_order_db_data
```

---

## Summary

✅ **Your data is SAFE when:**
- Container stops
- Container is removed  
- You run `docker compose down`
- You run `docker compose restart`

❌ **Your data is DELETED when:**
- You run `docker compose down -v`
- You manually delete the volume: `docker volume rm ...`
- You run `docker volume prune` and confirm

**Default behavior = DATA PERSISTS** 🎉
