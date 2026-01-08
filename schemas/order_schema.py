"""Order schema with validation and separate create/update schemas."""
from datetime import datetime
from typing import Optional
from pydantic import Field

from schemas.base_schema import BaseSchema
from models.enums import DeliveryMethod, Status


class OrderBaseSchema(BaseSchema):
    """Base schema for Order with common fields."""
    
    date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Order date"
    )
    total: Optional[float] = Field(
        None,
        ge=0,
        description="Total amount (must be >= 0)"
    )
    delivery_method: Optional[DeliveryMethod] = Field(
        None,
        description="Delivery method"
    )
    status: Optional[Status] = Field(
        default=Status.PENDING,
        description="Order status"
    )
    client_id: Optional[int] = Field(
        None,
        description="Client ID reference"
    )

    # ⚠️ IMPORTANTE: bill_id opcional
    bill_id: Optional[int] = Field(
        None,
        description="Bill ID reference"
    )


class OrderCreateSchema(OrderBaseSchema):
    """Schema for creating a new order (required fields)."""

    total: float = Field(..., ge=0, description="Total amount (required)")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method (required)")
    client_id: int = Field(..., description="Client ID reference (required)")

    # ❌ QUITAMOS bill_id de aquí
    bill_id: Optional[int] = None


class OrderUpdateSchema(OrderBaseSchema):
    """Schema for updating an order (all fields optional)."""
    pass


class OrderSchema(OrderBaseSchema):
    """Complete schema for Order entity (for responses)."""

    id_key: int
    date: datetime
    total: float
    delivery_method: DeliveryMethod
    status: Status
    client_id: int
