"""Order controller implementation."""
from typing import List
from fastapi import Depends, HTTPException # ✅ Importar HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from config.database import get_db
from controllers.base_controller_impl import BaseControllerImpl
# ✅ Importamos el nuevo esquema OrderStatusUpdate
from schemas.order_schema import OrderSchema, OrderCreateSchema, OrderUpdateSchema, OrderStatusUpdate
from services.order_service import OrderService
from models.order import OrderModel

class OrderController(BaseControllerImpl):
    def __init__(self):
        super().__init__(
            schema=OrderSchema,
            create_schema=OrderCreateSchema,
            update_schema=OrderUpdateSchema,
            service_factory=lambda db: OrderService(db),
            tags=["Orders"]
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        
        # Ruta existente (Historial del cliente)
        @self.router.get("/client/{client_id}", response_model=List[OrderSchema])
        async def get_orders_by_client(client_id: int, db: Session = Depends(get_db)):
            stmt = (
                select(OrderModel)
                .where(OrderModel.client_id == client_id)
                .order_by(desc(OrderModel.date))
            )
            orders = db.execute(stmt).scalars().all()
            return orders

        # ✅ NUEVA RUTA: PATCH solo para el estado
        # Esta ruta es "a prueba de balas" porque no valida el resto de campos (total, cliente, etc)
        @self.router.patch("/id/{id}/status", response_model=OrderSchema)
        async def update_order_status(id: int, status_data: OrderStatusUpdate, db: Session = Depends(get_db)):
            service = self.service_factory(db)
            # Buscamos la orden
            order = service.get_by_id(id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Actualizamos solo el estado
            order.status = status_data.status
            db.commit()
            db.refresh(order)
            return order