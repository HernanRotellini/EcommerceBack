"""Client schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import EmailStr, Field

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.address_schema import AddressSchema
    from schemas.order_schema import OrderSchema


class ClientSchema(BaseSchema):
    """Schema for Client entity with validations."""

    name: str = Field(..., min_length=1, max_length=100, description="Client's first name")
    lastname: str = Field(..., min_length=1, max_length=100, description="Client's last name")
    email: EmailStr = Field(..., description="Client's email address")
    telephone: Optional[str] = Field(
        None,
        description="Client's phone number"
    )
    password: str = Field(..., min_length=1, description="Client's password")
    is_admin: bool = Field(default=False, description="Whether the client is an admin")
