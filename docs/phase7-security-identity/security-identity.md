# Phase 7: Security & Identity

## Overview

Security in distributed systems requires defense-in-depth: multiple layers of protection that work together. This phase covers authentication, authorization, secrets management, and security best practices for building secure distributed systems.

**Key Principle:** Never trust, always verify. Assume breach and minimize blast radius.

---

## Table of Contents

1. [Authentication & Authorization](#1-authentication--authorization)
2. [OAuth 2.0 and OpenID Connect](#2-oauth-20-and-openid-connect)
3. [Secrets Management](#3-secrets-management)
4. [API Security](#4-api-security)
5. [Zero Trust Architecture](#5-zero-trust-architecture)

---

## 1. Authentication & Authorization

### 1.1 Definitions

**Authentication (AuthN):** Who are you?
- Verifying identity
- Login with username/password, OAuth, SSO

**Authorization (AuthZ):** What can you do?
- Verifying permissions
- Role-Based Access Control (RBAC), Attribute-Based Access Control (ABAC)

### 1.2 JWT (JSON Web Tokens)

**Structure:**
```
Header.Payload.Signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Decoded:**
```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "roles": ["user", "admin"],
  "iat": 1516239022,
  "exp": 1516242622
}

// Signature
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

**Implementation:**

```python
import jwt
from datetime import datetime, timedelta
from typing import Dict, List

SECRET_KEY = "your-secret-key-keep-it-safe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_id: str, roles: List[str]) -> str:
    """Create a JWT access token"""
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> Dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


# Usage in API
from fastapi import HTTPException, Depends, Header

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        payload = verify_token(token)
        return payload

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/orders")
async def create_order(
    order_data: dict,
    current_user: dict = Depends(get_current_user)
):
    # current_user contains decoded JWT payload
    user_id = current_user["sub"]
    roles = current_user["roles"]

    # Create order for authenticated user
    return create_order_for_user(user_id, order_data)
```

**JWT Best Practices:**

```python
# ✅ DO: Use short expiration times
ACCESS_TOKEN_EXPIRE = 15  # minutes
REFRESH_TOKEN_EXPIRE = 7   # days

# ✅ DO: Include minimal claims
payload = {
    "sub": user_id,
    "roles": ["user"],
    "exp": expiration
}
# Don't include sensitive data (passwords, SSN, etc.)

# ✅ DO: Use RS256 for production (asymmetric)
# Public key to verify, private key to sign
import jwt
from cryptography.hazmat.primitives import serialization

# Sign with private key
with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(), password=None
    )

token = jwt.encode(payload, private_key, algorithm="RS256")

# Verify with public key
with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

payload = jwt.decode(token, public_key, algorithms=["RS256"])


# ❌ DON'T: Store sensitive data in JWT
payload = {
    "password": "secret123",  # NEVER!
    "credit_card": "1234-5678-9012-3456"  # NEVER!
}

# ❌ DON'T: Use HS256 with weak secret
SECRET_KEY = "secret"  # Too weak, easily cracked
```

---

### 1.3 Session-Based Authentication

**Session Store:**

```python
import redis
import secrets
from datetime import timedelta

class SessionStore:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.session_ttl = timedelta(hours=24)

    def create_session(self, user_id: str) -> str:
        """Create a new session and return session ID"""
        session_id = secrets.token_urlsafe(32)

        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }

        # Store in Redis with TTL
        self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            json.dumps(session_data)
        )

        return session_id

    def get_session(self, session_id: str) -> dict:
        """Get session data and update last activity"""
        data = self.redis.get(f"session:{session_id}")

        if not data:
            return None

        session = json.loads(data)

        # Update last activity
        session["last_activity"] = datetime.utcnow().isoformat()
        self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            json.dumps(session)
        )

        return session

    def delete_session(self, session_id: str):
        """Delete session (logout)"""
        self.redis.delete(f"session:{session_id}")


# Usage with cookies
from fastapi import Response, Cookie

session_store = SessionStore()

@app.post("/login")
async def login(credentials: dict, response: Response):
    # Verify credentials
    user = authenticate_user(credentials["username"], credentials["password"])

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    session_id = session_store.create_session(user["id"])

    # Set cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # Only send over HTTPS
        samesite="strict"  # CSRF protection
    )

    return {"message": "Logged in successfully"}


@app.get("/profile")
async def get_profile(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = session_store.get_session(session_id)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = get_user(session["user_id"])
    return user
```

---

### 1.4 Role-Based Access Control (RBAC)

```python
from enum import Enum
from typing import List, Set

class Permission(Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    READ_ORDERS = "read:orders"
    WRITE_ORDERS = "write:orders"
    READ_ADMIN = "read:admin"

class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.USER: {
        Permission.READ_USERS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS
    },
    Role.MODERATOR: {
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS
    },
    Role.ADMIN: {
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS,
        Permission.READ_ADMIN
    }
}

def get_permissions(roles: List[str]) -> Set[Permission]:
    """Get all permissions for given roles"""
    permissions = set()
    for role_str in roles:
        role = Role(role_str)
        permissions.update(ROLE_PERMISSIONS.get(role, set()))
    return permissions


# Decorator for permission checking
from functools import wraps

def require_permission(required_permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")

            user_permissions = get_permissions(current_user.get("roles", []))

            if required_permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required permission: {required_permission.value}"
                )

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# Usage
@app.delete("/api/users/{user_id}")
@require_permission(Permission.DELETE_USERS)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    # Only users with DELETE_USERS permission can access
    delete_user_from_db(user_id)
    return {"message": "User deleted"}
```

---

## 2. OAuth 2.0 and OpenID Connect

### 2.1 OAuth 2.0 Flow

**Authorization Code Flow (most common):**

```
User → Client App → Authorization Server → Resource Server

1. User clicks "Login with Google"
2. Client redirects to Authorization Server (Google)
3. User authenticates and grants permission
4. Authorization Server redirects back with authorization code
5. Client exchanges code for access token
6. Client uses access token to access Resource Server (APIs)
```

**Implementation:**

```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Configuration
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Routes
@app.get('/login')
async def login(request: Request):
    # Redirect to Google's authorization page
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth/callback')
async def auth_callback(request: Request):
    # Exchange authorization code for access token
    token = await oauth.google.authorize_access_token(request)

    # Get user info using access token
    user_info = await oauth.google.parse_id_token(request, token)

    # Create session for user
    session_id = session_store.create_session(user_info['sub'])

    # Set cookie and redirect
    response = RedirectResponse(url='/')
    response.set_cookie('session_id', session_id, httponly=True, secure=True)

    return response
```

---

### 2.2 Service-to-Service Authentication (mTLS)

**Mutual TLS:** Both client and server verify each other's certificates.

```python
import requests

# Client-side: Use client certificate
response = requests.get(
    'https://api.example.com/data',
    cert=('/path/to/client.crt', '/path/to/client.key'),
    verify='/path/to/ca-bundle.crt'
)
```

**Server-side configuration (nginx):**

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    # Server certificate
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # Require client certificate
    ssl_client_certificate /etc/nginx/ssl/ca.crt;
    ssl_verify_client on;

    location / {
        # Extract client certificate info
        proxy_set_header X-Client-CN $ssl_client_s_dn_cn;
        proxy_set_header X-Client-Verified $ssl_client_verify;

        proxy_pass http://backend;
    }
}
```

---

## 3. Secrets Management

### 3.1 HashiCorp Vault

**Setup and usage:**

```python
import hvac

# Initialize Vault client
client = hvac.Client(url='http://vault:8200')

# Authenticate (using AppRole for services)
client.auth.approle.login(
    role_id='your-role-id',
    secret_id='your-secret-id'
)

# Read secret
secret = client.secrets.kv.v2.read_secret_version(
    path='database/credentials',
    mount_point='secret'
)

db_username = secret['data']['data']['username']
db_password = secret['data']['data']['password']

# Write secret
client.secrets.kv.v2.create_or_update_secret(
    path='api-keys/stripe',
    secret={'api_key': 'sk_live_...'},
    mount_point='secret'
)

# Dynamic secrets (generated on-demand)
# Database credentials that auto-expire
db_creds = client.secrets.database.generate_credentials(
    name='my-database-role'
)

# Use credentials
connection = psycopg2.connect(
    host='database',
    user=db_creds['data']['username'],
    password=db_creds['data']['password'],
    database='myapp'
)
```

---

### 3.2 Secrets in Environment Variables

**Best practices:**

```python
import os
from dotenv import load_dotenv

# Load from .env file (development only)
load_dotenv()

# Access secrets
DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('API_KEY')
JWT_SECRET = os.getenv('JWT_SECRET')

# Validate required secrets
required_secrets = ['DATABASE_URL', 'API_KEY', 'JWT_SECRET']
missing = [s for s in required_secrets if not os.getenv(s)]

if missing:
    raise Exception(f"Missing required secrets: {', '.join(missing)}")


# ❌ NEVER commit .env to version control
# Add to .gitignore:
# .env
# .env.local
# .env.production

# ✅ Provide .env.example template:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# API_KEY=your_api_key_here
# JWT_SECRET=your_jwt_secret_here
```

**Kubernetes Secrets:**

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  # Base64 encoded values
  database-url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BkYjo1NDMyL2RiCg==
  api-key: c2tfbGl2ZV8xMjM0NTY3ODkwCg==

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        env:
          # Inject secrets as environment variables
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: database-url
          - name: API_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: api-key
```

---

### 3.3 Key Rotation

```python
import time
from typing import Dict

class RotatingKeyManager:
    def __init__(self, rotation_interval_seconds=86400):  # 24 hours
        self.rotation_interval = rotation_interval_seconds
        self.keys = {}
        self.current_key_id = None
        self.last_rotation = None

    def rotate_key(self):
        """Generate new key and mark as current"""
        new_key_id = f"key-{int(time.time())}"
        new_key = generate_secure_key()  # Your key generation logic

        # Add new key
        self.keys[new_key_id] = {
            'key': new_key,
            'created_at': time.time(),
            'status': 'active'
        }

        # Mark old key as retired (but keep for verification)
        if self.current_key_id:
            self.keys[self.current_key_id]['status'] = 'retired'

        self.current_key_id = new_key_id
        self.last_rotation = time.time()

        # Clean up very old keys (older than 7 days)
        cutoff = time.time() - (7 * 86400)
        self.keys = {
            kid: data for kid, data in self.keys.items()
            if data['created_at'] > cutoff
        }

    def get_current_key(self):
        """Get key for signing"""
        if not self.current_key_id or self.should_rotate():
            self.rotate_key()

        return self.current_key_id, self.keys[self.current_key_id]['key']

    def get_key(self, key_id: str):
        """Get key for verification (may be retired)"""
        if key_id not in self.keys:
            raise Exception(f"Unknown key: {key_id}")

        return self.keys[key_id]['key']

    def should_rotate(self):
        """Check if key should be rotated"""
        if not self.last_rotation:
            return True

        return (time.time() - self.last_rotation) > self.rotation_interval


# Usage with JWT
key_manager = RotatingKeyManager()

def create_token(payload: dict) -> str:
    key_id, key = key_manager.get_current_key()

    # Include key ID in JWT header
    headers = {'kid': key_id}

    token = jwt.encode(payload, key, algorithm='HS256', headers=headers)
    return token

def verify_token(token: str) -> dict:
    # Decode header to get key ID
    unverified_header = jwt.get_unverified_header(token)
    key_id = unverified_header['kid']

    # Get appropriate key for verification
    key = key_manager.get_key(key_id)

    # Verify token
    payload = jwt.decode(token, key, algorithms=['HS256'])
    return payload
```

---

## 4. API Security

### 4.1 Rate Limiting

```python
from redis import Redis
from time import time

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Token bucket algorithm for rate limiting.

        Args:
            key: Identifier (e.g., user_id, IP address)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = time()
        window_key = f"rate_limit:{key}:{int(now // window_seconds)}"

        current = self.redis.incr(window_key)

        if current == 1:
            # First request in this window, set expiration
            self.redis.expire(window_key, window_seconds)

        return current <= max_requests


# Middleware
from fastapi import Request, HTTPException

rate_limiter = RateLimiter(redis_client)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Identify client (by IP or user ID)
    client_id = request.client.host

    # Check rate limit: 100 requests per minute
    if not rate_limiter.is_allowed(client_id, max_requests=100, window_seconds=60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"}
        )

    response = await call_next(request)
    return response


# Per-endpoint rate limiting
def rate_limit(max_requests: int, window_seconds: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_id = request.client.host

            if not rate_limiter.is_allowed(client_id, max_requests, window_seconds):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.post("/api/expensive-operation")
@rate_limit(max_requests=10, window_seconds=3600)  # 10 per hour
async def expensive_operation():
    pass
```

---

### 4.2 Input Validation

```python
from pydantic import BaseModel, validator, EmailStr
from typing import Optional
import re

class UserCreateRequest(BaseModel):
    email: EmailStr  # Automatically validates email format
    password: str
    username: str
    age: Optional[int] = None

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')

        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')

        return v

    @validator('username')
    def username_valid(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', v):
            raise ValueError(
                'Username must be 3-20 characters, '
                'alphanumeric, underscore, or hyphen'
            )
        return v

    @validator('age')
    def age_valid(cls, v):
        if v is not None and (v < 13 or v > 120):
            raise ValueError('Age must be between 13 and 120')
        return v


# API endpoint
@app.post("/api/users")
async def create_user(user_data: UserCreateRequest):
    # Pydantic automatically validates request body
    # If validation fails, returns 422 with error details

    # Hash password before storing
    hashed_password = hash_password(user_data.password)

    user = {
        "email": user_data.email,
        "username": user_data.username,
        "password": hashed_password,
        "age": user_data.age
    }

    save_user(user)
    return {"message": "User created"}
```

---

### 4.3 SQL Injection Prevention

```python
import psycopg2

# ❌ VULNERABLE to SQL injection
def get_user_unsafe(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    # If username is "admin' OR '1'='1", returns all users!

# ✅ SAFE: Use parameterized queries
def get_user_safe(username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    # Database driver escapes parameters

# ✅ SAFE: Use ORM (SQLAlchemy)
from sqlalchemy.orm import Session
from models import User

def get_user_orm(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()
    # ORM automatically parameterizes queries
```

---

### 4.4 CORS (Cross-Origin Resource Sharing)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",      # Production frontend
        "http://localhost:3000"          # Development frontend
    ],
    allow_credentials=True,              # Allow cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600                         # Cache preflight for 1 hour
)

# ❌ DON'T: Allow all origins in production
# allow_origins=["*"]  # Only for public APIs
```

---

## 5. Zero Trust Architecture

### 5.1 Principles

1. **Never trust, always verify**
2. **Assume breach**
3. **Verify explicitly**
4. **Use least privilege access**
5. **Segment access**

### 5.2 Implementation

```python
# Service-to-service authentication with JWT
class ServiceAuthMiddleware:
    def __init__(self, app, required_service: str = None):
        self.app = app
        self.required_service = required_service

    async def __call__(self, request: Request, call_next):
        # Extract service token
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing service authentication"}
            )

        try:
            # Verify service token
            token = auth_header.replace('Bearer ', '')
            payload = verify_service_token(token)

            # Check if this service is allowed to call this endpoint
            service_name = payload['service']

            if self.required_service and service_name != self.required_service:
                return JSONResponse(
                    status_code=403,
                    content={"error": f"Service {service_name} not allowed"}
                )

            # Add service info to request state
            request.state.service = service_name

            response = await call_next(request)
            return response

        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"error": str(e)}
            )


# Apply to app
app.add_middleware(
    ServiceAuthMiddleware,
    required_service=None  # Verify all services, allow any authenticated
)


# Network policies (Kubernetes)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Only allow traffic from frontend
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  # Only allow traffic to database and cache
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

---

## Summary and Key Takeaways

### Authentication
- **JWT:** Stateless, scalable, but can't be revoked easily
- **Sessions:** Stateful, easy to revoke, but requires shared state
- **OAuth 2.0:** Delegate authentication to trusted providers
- **mTLS:** Strong service-to-service authentication

### Authorization
- **RBAC:** Simple, role-based permissions
- **ABAC:** Complex, attribute-based policies
- **Principle of least privilege:** Grant minimum required permissions

### Secrets Management
- Never hardcode secrets in code
- Use environment variables or secret management tools
- Rotate keys regularly
- Use different secrets for different environments

### API Security
- **Rate limiting:** Prevent abuse
- **Input validation:** Prevent injection attacks
- **CORS:** Control cross-origin requests
- **HTTPS:** Encrypt data in transit

### Zero Trust
- Verify every request
- Assume network is hostile
- Segment access
- Monitor everything

---

## Additional Resources

### Tools
- **Auth:** Auth0, Okta, Keycloak
- **Secrets:** HashiCorp Vault, AWS Secrets Manager, Google Secret Manager
- **API Gateway:** Kong, Envoy, AWS API Gateway

### Standards
- OAuth 2.0: https://oauth.net/2/
- OpenID Connect: https://openid.net/connect/
- JWT: https://jwt.io

### Books
- "OAuth 2 in Action" by Justin Richer
- "Zero Trust Networks" by Evan Gilman
