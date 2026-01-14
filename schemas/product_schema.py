from typing import Optional, List, TYPE_CHECKING
from pydantic import Field, ConfigDict
from schemas.base_schema import BaseSchema
from schemas.category_schema import CategoryBaseSchema

if TYPE_CHECKING:
    from schemas.review_schema import ReviewSchema

# Esquema Base
class ProductBaseSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None)
    category_id: Optional[int] = Field(None)
    active: bool = True # ✅ Nuevo campo

# ✅ Esquemas LIMPIOS para escritura (Soluciona error 400 en PUT/POST)
class ProductCreateSchema(ProductBaseSchema):
    pass

class ProductUpdateSchema(ProductBaseSchema):
    pass

# Esquema Completo para Lectura (Incluye relaciones)
class ProductSchema(ProductBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    
    category: Optional[CategoryBaseSchema] = None
    reviews: Optional[List['ReviewSchema']] = []

class ProductAdminSchema(ProductBaseSchema):
    pass