from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field
from schemas.base_schema import BaseSchema
from models.enums import DeliveryMethod, Status

if TYPE_CHECKING:
    from schemas.client_schema import ClientSchema
    from schemas.bill_schema import BillSchema
    from schemas.order_detail_schema import OrderDetailSchema

# 1. BASE
class OrderBaseSchema(BaseSchema):
    total: float = Field(..., ge=0)
    delivery_method: DeliveryMethod = Field(...)
    client_id: int = Field(...)
    bill_id: int = Field(...)

# 2. CREATE
class OrderCreateSchema(OrderBaseSchema):
    pass

# 3. UPDATE (✅ NUEVO: Permite cambiar el estado)
class OrderUpdateSchema(BaseSchema):
    total: Optional[float] = None
    delivery_method: Optional[DeliveryMethod] = None
    status: Optional[Status] = None  # ✅ Esto habilita el cambio desde el Admin
    
# 4. RESPONSE
class OrderSchema(OrderBaseSchema):
    id_key: int
    date: datetime
    status: Status
    
    client: Optional["ClientSchema"] = None
    bill: Optional["BillSchema"] = None
    details: List["OrderDetailSchema"] = []
    
    class Config:
        from_attributes = True