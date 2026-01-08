"""Login schemas for authentication."""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(..., description="Client's email address")
    password: str = Field(..., min_length=1, description="Client's password")


class LoginResponse(BaseModel):
    """Schema for login response."""
    id_key: int
    name: str
