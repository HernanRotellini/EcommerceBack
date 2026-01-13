"""Order controller with proper dependency injection."""
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from config.database import get_db
from controllers.base_controller_impl import BaseControllerImpl
from schemas.order_schema import OrderSchema
from services.order_service import OrderService
from models.order import OrderModel

class OrderController(BaseControllerImpl):
    """Controller for Order entity with CRUD operations."""

    def __init__(self):
        super().__init__(
            schema=OrderSchema,
            service_factory=lambda db: OrderService(db),
            tags=["Orders"]
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        
        # --- NUEVO ENDPOINT: Historial de compras del cliente ---
        @self.router.get("/client/{client_id}", response_model=List[OrderSchema])
        async def get_orders_by_client(client_id: int, db: Session = Depends(get_db)):
            # Buscamos órdenes del cliente, ordenadas por fecha (más reciente primero)
            # SQLAlchemy resolverá automáticamente las relaciones (details -> product) si están configuradas en el modelo
            stmt = (
                select(OrderModel)
                .where(OrderModel.client_id == client_id)
                .order_by(desc(OrderModel.date))
            )
            orders = db.execute(stmt).scalars().all()
            return orders