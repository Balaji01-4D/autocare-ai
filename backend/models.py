from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from decimal import Decimal
from datetime import datetime


class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    door_no: str
    street: str
    city: str
    state: str
    zipcode: str
    
    # One-to-one relationship with User
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", unique=True)
    user: Optional["User"] = Relationship(back_populates="address")

    # Optional: string representation
    def __str__(self):
        return f"{self.door_no}, {self.street}, {self.city}, {self.state} - {self.zipcode}"


class User(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("email"),
        UniqueConstraint("number"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, nullable=False)
    number: str = Field(index=True, nullable=False)
    password: str
    
    # One-to-one relationship with Address
    address: Optional[Address] = Relationship(back_populates="user")


# Chat-related models for conversation memory
class ChatConversation(SQLModel, table=True):
    """
    Stores chat conversation sessions per user
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    session_id: str = Field(index=True)  # To group related messages
    title: Optional[str] = Field(default=None)  # Auto-generated conversation title
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["ChatMessage"] = Relationship(back_populates="conversation")


class ChatMessage(SQLModel, table=True):
    """
    Stores individual messages within conversations
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="chatconversation.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Message content
    message: str = Field(index=True)  # User's message
    response: Optional[str] = Field(default=None)  # Bot's response
    sender: str = Field(default="user")  # "user" or "bot"
    
    # Context data
    selected_cars: Optional[str] = Field(default=None)  # JSON string of car IDs
    context_used: Optional[str] = Field(default=None)  # What context was used for response
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: Optional[ChatConversation] = Relationship(back_populates="messages")


class ChatMemoryEntry(SQLModel, table=True):
    """
    Stores preprocessed memory entries for RAG retrieval
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    conversation_id: int = Field(foreign_key="chatconversation.id")
    message_id: int = Field(foreign_key="chatmessage.id")
    
    # Content for RAG
    content: str = Field(index=True)  # Preprocessed content for similarity search
    keywords: Optional[str] = Field(default=None)  # Extracted keywords
    intent: Optional[str] = Field(default=None)  # Classified intent (comparison, info, etc.)
    car_models_mentioned: Optional[str] = Field(default=None)  # JSON array of mentioned models
    
    # Relevance scoring
    importance_score: float = Field(default=0.5)  # 0-1 score for importance
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Car-related models
class Car(SQLModel, table=True):
    """Main Car model containing all car information"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic car information
    model_name: str = Field(index=True)
    model_year: int = Field(index=True)
    trim_variant: str
    body_type: str
    
    # Dimensions (in mm)
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    wheelbase_mm: Optional[int] = None
    curb_weight_kg: Optional[int] = None
    
    # Engine specifications
    engine_type: str
    displacement_cc: Optional[int] = None
    cylinders: str
    horsepower_hp: Optional[int] = None
    torque_nm: Optional[int] = None
    
    # Drivetrain
    transmission: str
    drivetrain: str
    
    # Performance
    acceleration_0_100_s: Optional[Decimal] = Field(default=None, max_digits=4, decimal_places=1)
    top_speed_kmh: Optional[int] = None
    fuel_consumption_combined: Optional[Decimal] = Field(default=None, max_digits=4, decimal_places=1)
    co2_emissions: Optional[int] = None
    electric_range_km: Optional[int] = None
    
    # Features and equipment
    infotainment: Optional[str] = None
    safety_features: Optional[str] = None
    wheel_sizes_available: Optional[str] = None
    
    # Colors (stored as comma-separated strings for simplicity)
    exterior_colors_available: Optional[str] = None
    interior_materials_colors: Optional[str] = None
    
    # Pricing
    base_msrp_usd: Optional[int] = None
    
    # Media
    image_link: Optional[str] = None
    
    # Unique constraint on model_name, model_year, and trim_variant
    __table_args__ = (
        UniqueConstraint("model_name", "model_year", "trim_variant"),
    )
    
    def get_composite_id(self) -> str:
        """Get a composite identifier for the car"""
        return f"{self.model_name}_{self.model_year}_{self.trim_variant}"
    
    def get_exterior_colors_list(self) -> List[str]:
        """Get exterior colors as a list"""
        if self.exterior_colors_available:
            return [color.strip() for color in self.exterior_colors_available.split(',')]
        return []
    
    def get_interior_colors_list(self) -> List[str]:
        """Get interior colors/materials as a list"""
        if self.interior_materials_colors:
            return [color.strip() for color in self.interior_materials_colors.split(',')]
        return []
    
    def get_safety_features_list(self) -> List[str]:
        """Get safety features as a list"""
        if self.safety_features:
            return [feature.strip() for feature in self.safety_features.split(',')]
        return []
    
    def get_wheel_sizes_list(self) -> List[str]:
        """Get wheel sizes as a list"""
        if self.wheel_sizes_available:
            return [size.strip() for size in self.wheel_sizes_available.split(',')]
        return []
    
    def __str__(self):
        return f"{self.model_year} {self.model_name} {self.trim_variant}"