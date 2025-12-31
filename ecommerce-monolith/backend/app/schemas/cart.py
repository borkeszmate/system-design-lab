from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import List, Optional


# Cart Item Schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(CartItemBase):
    id: int
    cart_id: int
    price_snapshot: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    subtotal: float
    # Include product details - TIGHT COUPLING!
    # In microservices, frontend would make separate call for product info
    product_name: Optional[str] = None
    product_image: Optional[str] = None

    class Config:
        from_attributes = True


# Cart Schemas
class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
