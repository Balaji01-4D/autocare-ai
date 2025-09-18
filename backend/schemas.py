from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class AddressCreate(BaseModel):
    door_no: str = Field(..., min_length=1, max_length=50)
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    zipcode: str = Field(..., min_length=5, max_length=10)

class AddressResponse(BaseModel):
    id: Optional[int] = None
    door_no: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    number: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8, max_length=100)
    door_no: str = Field(..., min_length=1, max_length=50)
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    zipcode: str = Field(..., min_length=5, max_length=10)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    number: str
    address: Optional[AddressResponse] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class AuthResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserProfileResponse(BaseModel):
    user: UserResponse

# Legacy schemas for backward compatibility
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    number: str
    password: str
    address: AddressCreate

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    number: str
    password: str
    door_no: str
    street: str
    city: str
    state: str
    zipcode: str

# Car related schemas
class CarResponse(BaseModel):
    id: str
    name: str
    model: str
    year: int
    price: int
    image: Optional[str] = None
    features: Optional[List[str]] = None
    engine: Optional[str] = None
    fuel_type: Optional[str] = None

class CarsListResponse(BaseModel):
    cars: List[CarResponse]
    user: Optional[UserResponse] = None  # Optional for public access
    timestamp: datetime

# Chatbot related schemas
class ChatbotRequest(BaseModel):
    message: str
    selected_cars: Optional[List[str]] = []  # List of car IDs

class ChatbotResponse(BaseModel):
    response: str
    user: Optional[UserResponse] = None  # Optional for non-authenticated users
    timestamp: datetime
    selected_cars_info: Optional[List[CarResponse]] = None
