from typing import Optional, List, TYPE_CHECKING
from pydantic import Field
from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.category_schema import CategorySchema


class ProductBaseSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    image_url: Optional[str] = None
    category_id: int

class ProductCreateSchema(ProductBaseSchema):
    pass

class ProductSchema(ProductBaseSchema):
    id_key: int

    category: Optional["CategorySchema"] = None
    # order_details: List["OrderDetailSchema"] = [] 
