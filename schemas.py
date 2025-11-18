"""
Database Schemas for Lele's Boutique

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class Lead(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    message: Optional[str] = Field(None, description="Inquiry message")
    source: Optional[str] = Field("website", description="Lead source")

class Booking(BaseModel):
    name: str = Field(...)
    email: EmailStr
    phone: Optional[str] = None
    service: str = Field(...)
    date: str = Field(..., description="Requested date/time as ISO string")
    notes: Optional[str] = None

class Service(BaseModel):
    title: str
    description: Optional[str] = None
    price_from: Optional[float] = Field(None, ge=0)
    duration_min: Optional[int] = Field(None, ge=0)

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    image: Optional[str] = None
    tag: Optional[str] = None

class Testimonial(BaseModel):
    name: str
    quote: str
    avatar: Optional[str] = None

class Post(BaseModel):
    title: str
    excerpt: Optional[str] = None
    image: Optional[str] = None
    published_at: Optional[datetime] = None
