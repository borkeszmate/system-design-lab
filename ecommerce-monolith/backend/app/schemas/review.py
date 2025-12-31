from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)  # 1-5 stars
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    product_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: int
    product_id: int
    user_id: int
    user_name: Optional[str] = None  # Include user name - COUPLING!
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    read: bool = True
