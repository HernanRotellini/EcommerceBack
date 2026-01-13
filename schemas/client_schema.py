"""Client schema for request/response validation."""
from typing import Optional
from pydantic import EmailStr, Field, ConfigDict
from schemas.base_schema import BaseSchema


class ClientBaseSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    telephone: Optional[str] = Field(None)
    is_admin: bool = Field(default=False)

class ClientCreateSchema(ClientBaseSchema):
    password: str = Field(..., min_length=1)


class ClientUpdateSchema(BaseSchema):
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    password: Optional[str] = None

class ClientSchema(ClientBaseSchema):
    id_key: int
    model_config = ConfigDict(from_attributes=True)