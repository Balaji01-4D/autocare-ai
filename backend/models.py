from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint


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