from typing import Optional, Union
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User, Address
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from security import (
    validate_password_strength, 
    validate_email_format, 
    validate_phone_number,
    sanitize_string,
    check_rate_limit,
    add_failed_attempt
)

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DB_URL", "sqlite:///./autocare.db")
engine = create_engine(DATABASE_URL, echo=False)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
if SECRET_KEY == "your-secret-key-change-in-production":
    print("WARNING: Using default SECRET_KEY. Change this in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type_check: str = payload.get("type")
        
        if user_id is None or token_type_check != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    with Session(engine) as session:
        user = session.get(User, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

def register_user_controller(
    name: str,
    email: str,
    number: str,
    password: str,
    door_no: str,
    street: str,
    city: str,
    state: str,
    zipcode: str
) -> dict:
    """
    Controller function to register a new user with address
    """
    # Input validation and sanitization
    name = sanitize_string(name, 100)
    email = sanitize_string(email.lower(), 255)
    number = sanitize_string(number, 15)
    door_no = sanitize_string(door_no, 50)
    street = sanitize_string(street, 200)
    city = sanitize_string(city, 100)
    state = sanitize_string(state, 100)
    zipcode = sanitize_string(zipcode, 10)
    
    # Validate input formats
    if not validate_email_format(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    if not validate_phone_number(number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format"
        )
    
    if not validate_password_strength(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        existing_number = session.exec(select(User).where(User.number == number)).first()
        if existing_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists"
            )
        
        try:
            # Create user
            user = User(
                name=name,
                email=email,
                number=number,
                password=hash_password(password)
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Create address
            address = Address(
                door_no=door_no,
                street=street,
                city=city,
                state=state,
                zipcode=zipcode,
                user_id=user.id
            )
            
            session.add(address)
            session.commit()
            session.refresh(address)
            
            # Create tokens
            access_token = create_access_token(data={"sub": str(user.id)})
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return {
                "message": "User registered successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "number": user.number,
                    "address": {
                        "id": address.id,
                        "door_no": address.door_no,
                        "street": address.street,
                        "city": address.city,
                        "state": address.state,
                        "zipcode": address.zipcode
                    }
                }
            }
            
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register user: {str(e)}"
            )

def login_user_controller(email: str, password: str) -> dict:
    """
    Controller function to authenticate user login with rate limiting
    """
    email = sanitize_string(email.lower(), 255)
    
    # Check rate limiting
    check_rate_limit(email)
    
    with Session(engine) as session:
        # Get user by email
        user = session.exec(select(User).where(User.email == email)).first()
        
        if not user or not verify_password(password, user.password):
            # Add failed attempt for rate limiting
            add_failed_attempt(email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Get user's address
        address = session.exec(select(Address).where(Address.user_id == user.id)).first()
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "number": user.number,
                "address": {
                    "id": address.id if address else None,
                    "door_no": address.door_no if address else None,
                    "street": address.street if address else None,
                    "city": address.city if address else None,
                    "state": address.state if address else None,
                    "zipcode": address.zipcode if address else None
                } if address else None
            }
        }

def refresh_token_controller(refresh_token: str) -> dict:
    """
    Controller function to refresh access token
    """
    try:
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        with Session(engine) as session:
            user = session.get(User, int(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            
            # Create new access token
            access_token = create_access_token(data={"sub": str(user.id)})
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_profile_controller(user_id: int) -> dict:
    """
    Controller function to get user profile
    """
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        address = session.exec(select(Address).where(Address.user_id == user.id)).first()
        
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "number": user.number,
                "address": {
                    "id": address.id if address else None,
                    "door_no": address.door_no if address else None,
                    "street": address.street if address else None,
                    "city": address.city if address else None,
                    "state": address.state if address else None,
                    "zipcode": address.zipcode if address else None
                } if address else None
            }
        }
