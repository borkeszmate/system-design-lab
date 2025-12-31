"""
User Service - Handles user authentication and profiles

This service handles:
- User registration
- User login (JWT tokens)
- User profile management
- Password hashing
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt

from .database import get_db, init_db
from . import models, schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "microservices-demo-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI(
    title="User Service",
    description="User authentication and profile management for E-commerce Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions
def hash_password(password: str) -> str:
    """Hash a password"""
    # Truncate password to 72 bytes for bcrypt
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes for bcrypt
    password_bytes = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(password_bytes.decode('utf-8'), hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 User Service starting up...")
    init_db()
    logger.info("✅ Database initialized")

    # Seed test user if database is empty
    db = next(get_db())
    user_count = db.query(models.User).count()
    if user_count == 0:
        logger.info("👤 Seeding test user...")
        test_user = models.User(
            email="paintest@example.com",
            name="Test User",
            password_hash=hash_password("password123")
        )
        db.add(test_user)
        db.commit()
        logger.info("✅ Test user created: paintest@example.com / password123")


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "User Service",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        logger.warning(f"❌ Registration failed: {user.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    db_user = models.User(
        email=user.email,
        name=user.name,
        password_hash=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"✅ User registered: {db_user.email}")
    return db_user


@app.post("/auth/login", response_model=schemas.TokenResponse)
async def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login and get JWT token"""
    # Find user
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user:
        logger.warning(f"❌ Login failed: User not found - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(f"❌ Login failed: Invalid password - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    logger.info(f"✅ User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserResponse)
async def get_current_user_profile(current_user: models.User = Depends(get_current_user)):
    """Get current user profile"""
    logger.info(f"👤 Profile retrieved: {current_user.email}")
    return current_user


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID (for internal service-to-service calls)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"👤 User retrieved: {user.email}")
    return user
