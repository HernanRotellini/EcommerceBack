from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field
from schemas.base_schema import BaseSchema
from models.enums import DeliveryMethod, Status

if TYPE_CHECKING:
    from schemas.client_schema import ClientSchema
    from schemas.bill_schema import BillSchema
    from schemas.order_detail_schema import OrderDetailSchema

# --- 1. BASE: Campos comunes ---
class OrderBaseSchema(BaseSchema):
    total: float = Field(..., ge=0, description="Total amount")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method (1: Store, 2: Carrier, 3: Home)")
    client_id: int = Field(..., description="Client ID")
    bill_id: int = Field(..., description="Bill ID")

# --- 2. CREATE: Lo que envía el Frontend (Sin fecha, ni estado) ---
class OrderCreateSchema(OrderBaseSchema):
    # Opcional: Si quieres permitir enviar fecha manual, ponlo Optional. 
    # Si no, déjalo vacío para usar defaults del Modelo.
    pass

# --- 3. RESPONSE: Lo que devuelve el Backend (Con todo) ---
class OrderSchema(OrderBaseSchema):
    id_key: int
    date: datetime # El backend la genera, aquí es obligatoria para mostrarla
    status: Status # El backend lo genera
    
    # Relaciones
    client: Optional["ClientSchema"] = None
    bill: Optional["BillSchema"] = None
    details: List["OrderDetailSchema"] = []