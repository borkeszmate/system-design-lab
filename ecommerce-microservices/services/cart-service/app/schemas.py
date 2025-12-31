"""Pydantic schemas for Cart Service"""
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional


class CartItemBase(BaseModel):
    """Base schema for Cart Item"""
    product_id: int
    quantity: int = 1


class CartItemCreate(CartItemBase):
    """Schema for adding item to cart"""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item"""
    quantity: int


class CartItemResponse(BaseModel):
    """Schema for cart item response"""
    id: int
    product_id: int
    product_name: str
    price: Decimal
    quantity: int

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema for cart response"""
    items: List[CartItemResponse]
    total: str
