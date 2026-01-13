from typing import Optional, List, TYPE_CHECKING
from pydantic import Field, ConfigDict
from schemas.base_schema import BaseSchema
from schemas.category_schema import CategoryBaseSchema

if TYPE_CHECKING:
    # from schemas.order_detail_schema import OrderDetailSchema  <-- COMENTAR O BORRAR
    from schemas.review_schema import ReviewSchema

class ProductBaseSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None)
    category_id: Optional[int] = Field(None)
    category: Optional[CategoryBaseSchema] = None

class ProductSchema(ProductBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    reviews: Optional[List['ReviewSchema']] = []
    


class ProductAdminSchema(ProductBaseSchema):
    pass