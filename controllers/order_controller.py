from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from config.database import get_db
from controllers.base_controller_impl import BaseControllerImpl
from schemas.order_schema import OrderSchema, OrderCreateSchema, OrderUpdateSchema, OrderStatusUpdate
from services.order_service import OrderService
from models.order import OrderModel
from models.enums import Status

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
        
        # Endpoint para historial de compras del cliente
        @self.router.get("/client/{client_id}", response_model=List[OrderSchema])
        async def get_orders_by_client(client_id: int, db: Session = Depends(get_db)):
            stmt = (
                select(OrderModel)
                .where(OrderModel.client_id == client_id)
                .order_by(desc(OrderModel.date))
            )
            orders = db.execute(stmt).scalars().all()
            return orders

        # Endpoint PATCH para actualizar solo el estado (Admin)
        @self.router.patch("/id/{id}/status", response_model=OrderSchema)
        async def update_order_status(id: int, status_data: OrderStatusUpdate, db: Session = Depends(get_db)):
            service = self.service_factory(db)
            
            # ✅ CORRECCIÓN: Usamos .read(id) porque get_by_id no existe en tu Service
            order = service.read(id)
            
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            try:
                # Convertimos el entero recibido al Enum Status
                new_status = Status(status_data.status)
                
                # Actualizamos y guardamos
                order.status = new_status
                db.commit()
                db.refresh(order)
                return order
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status value")