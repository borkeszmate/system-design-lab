"""Pydantic schemas for Product Service"""
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    """Base schema for Product"""
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int = 0


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
