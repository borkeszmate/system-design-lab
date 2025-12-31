from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    category_id: int
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    initial_inventory: int = 0  # Initial stock when creating product


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[condecimal(max_digits=10, decimal_places=2)] = None  # type: ignore
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Include inventory info - TIGHT COUPLING!
    # In microservices, inventory would be a separate API call
    available_stock: Optional[int] = None
    average_rating: Optional[float] = None
    review_count: Optional[int] = None

    class Config:
        from_attributes = True


# Inventory Schemas
class InventoryUpdate(BaseModel):
    quantity: int


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    reserved_quantity: int
    available: int

    class Config:
        from_attributes = True
