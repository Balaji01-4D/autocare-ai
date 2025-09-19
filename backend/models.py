from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from decimal import Decimal


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