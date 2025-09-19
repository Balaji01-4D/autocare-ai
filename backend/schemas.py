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
    id: int
    model_name: str
    model_year: int
    trim_variant: str
    body_type: str
    
    # Dimensions
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    wheelbase_mm: Optional[int] = None
    curb_weight_kg: Optional[int] = None
    
    # Engine specs
    engine_type: Optional[str] = None
    displacement_cc: Optional[int] = None
    cylinders: Optional[str] = None
    horsepower_hp: Optional[int] = None
    torque_nm: Optional[int] = None
    
    # Drivetrain
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    
    # Performance
    acceleration_0_100_s: Optional[float] = None
    top_speed_kmh: Optional[int] = None
    fuel_consumption_combined: Optional[float] = None
    co2_emissions: Optional[int] = None
    electric_range_km: Optional[int] = None
    
    # Features and colors
    infotainment: Optional[str] = None
    safety_features: Optional[List[str]] = None
    exterior_colors_available: Optional[List[str]] = None
    interior_materials_colors: Optional[List[str]] = None
    wheel_sizes_available: Optional[List[str]] = None
    
    # Pricing and media
    base_msrp_usd: Optional[int] = None
    image_link: Optional[str] = None
    
    # Computed display name
    display_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class CarsListResponse(BaseModel):
    cars: List[CarResponse]
    user: Optional[UserResponse] = None  # Optional for public access
    timestamp: datetime

# Lightweight schema for car comparison
class CarComparisonResponse(BaseModel):
    id: int
    model_name: str
    model_year: int
    trim_variant: str
    body_type: str
    base_msrp_usd: Optional[int] = None
    display_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class CarsComparisonListResponse(BaseModel):
    cars: List[CarComparisonResponse]
    limit: int
    total_available: int
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
