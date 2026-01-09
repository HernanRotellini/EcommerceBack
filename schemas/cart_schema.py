from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from schemas.product_schema import ProductSchema

# Lo que recibimos del Frontend para agregar un item
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Cantidad a agregar (mayor a 0)")

# Lo que devolvemos al Frontend (Item con datos del producto expandidos)
class CartItemResponse(CartItemBase):
    id_key: int
    product: Optional[ProductSchema] = None
    
    model_config = ConfigDict(from_attributes=True)

# El Carrito completo que devolvemos
class CartResponse(BaseModel):
    id_key: int
    client_id: int
    items: List[CartItemResponse] = []
    total: float = 0.0 # Este campo lo calcularemos en el controlador, no existe en BD
    
    model_config = ConfigDict(from_attributes=True)