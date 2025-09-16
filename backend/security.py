from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import re
import secrets
import string

def validate_password_strength(password: str) -> bool:
    """
    Validate password strength
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False
    
    if not re.search(r"[A-Z]", password):
        return False
    
    if not re.search(r"[a-z]", password):
        return False
    
    if not re.search(r"\d", password):
        return False
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    
    return True

def validate_email_format(email: str) -> bool:
    """
    Validate email format
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (basic validation)
    """
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it has 10-15 digits
    return 10 <= len(digits_only) <= 15

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def sanitize_string(text: str, max_length: int = 255) -> str:
    """
    Sanitize string input
    """
    # Remove any HTML tags and limit length
    sanitized = re.sub(r'<[^>]*>', '', text)
    return sanitized.strip()[:max_length]

class RateLimiter:
    """
    Simple in-memory rate limiter for login attempts
    In production, use Redis or similar
    """
    def __init__(self, max_attempts: int = 5, time_window: int = 300):
        self.max_attempts = max_attempts
        self.time_window = time_window  # 5 minutes
        self.attempts = {}
    
    def is_rate_limited(self, identifier: str) -> bool:
        """
        Check if identifier is rate limited
        """
        now = datetime.utcnow()
        
        if identifier not in self.attempts:
            return False
        
        # Clean old attempts
        self.attempts[identifier] = [
            attempt_time for attempt_time in self.attempts[identifier]
            if now - attempt_time < timedelta(seconds=self.time_window)
        ]
        
        return len(self.attempts[identifier]) >= self.max_attempts
    
    def add_attempt(self, identifier: str):
        """
        Add a failed attempt
        """
        now = datetime.utcnow()
        
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        self.attempts[identifier].append(now)

# Global rate limiter instance
login_rate_limiter = RateLimiter()

def check_rate_limit(identifier: str):
    """
    Check rate limit and raise exception if exceeded
    """
    if login_rate_limiter.is_rate_limited(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )

def add_failed_attempt(identifier: str):
    """
    Add failed login attempt
    """
    login_rate_limiter.add_attempt(identifier)
