"""Client schema for request/response validation."""
from typing import Optional
from pydantic import EmailStr, Field, ConfigDict
from schemas.base_schema import BaseSchema

# 1. BASE: Campos comunes (sin password, sin ID)
class ClientBaseSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    telephone: Optional[str] = Field(None)
    is_admin: bool = Field(default=False)

# 2. RESPONSE: Lo que el Frontend recibe (GET)
# ✅ IMPORTANTE: Agregamos ConfigDict para que lea el modelo de BD
class ClientResponseSchema(ClientBaseSchema):
    id_key: int
    
    # Configuración vital para Pydantic v2 + SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# 3. CREATE: Lo que se envía al registrarse (POST)
class ClientCreateSchema(ClientBaseSchema):
    password: str = Field(..., min_length=1, description="Password is required for creation")

# 4. UPDATE: Lo que se envía al editar (PUT) - Todo opcional
class ClientUpdateSchema(BaseSchema):
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    password: Optional[str] = None