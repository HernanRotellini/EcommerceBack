from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from config.database import get_db
from models.cart import CartModel, CartItemModel
from models.product import ProductModel
from schemas.cart_schema import CartResponse, CartItemBase

class CartController:
    def __init__(self):
        self.router = APIRouter(tags=["Cart"])
        self._register_routes()

    def _register_routes(self):
        
        # OBTENER CARRITO (GET /api/v1/cart/{client_id})
        @self.router.get("/{client_id}", response_model=CartResponse)
        async def get_cart(client_id: int, db: Session = Depends(get_db)):
            # Buscamos el carrito del cliente
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            
            # Si no tiene carrito, se lo creamos automáticamente ahora mismo
            if not cart:
                cart = CartModel(client_id=client_id)
                db.add(cart)
                db.commit()
                db.refresh(cart)
            
            # Calculamos el total en tiempo real (Precio actual * Cantidad)
            total = sum(item.quantity * item.product.price for item in cart.items if item.product)
            
            # Preparamos la respuesta
            response = CartResponse.model_validate(cart)
            response.total = total
            return response

        # AGREGAR ITEM (POST /api/v1/cart/{client_id}/items)
        @self.router.post("/{client_id}/items")
        async def add_item(client_id: int, item_data: CartItemBase, db: Session = Depends(get_db)):
            # 1. Aseguramos que exista el carrito
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart:
                cart = CartModel(client_id=client_id)
                db.add(cart)
                db.commit()
                db.refresh(cart)

            # 2. Verificamos el producto y su stock REAL
            product = db.query(ProductModel).get(item_data.product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            # 3. Buscamos si el item ya estaba en el carrito
            # (Usamos lógica en memoria para no hacer otra query compleja, ya que cart.items ya se cargó)
            existing_item = next((i for i in cart.items if i.product_id == item_data.product_id), None)
            
            if existing_item:
                # Si ya existe, sumamos la nueva cantidad a la anterior
                new_qty = existing_item.quantity + item_data.quantity
                
                # VALIDACIÓN BLANDA: No dejamos agregar más del stock existente
                if new_qty > product.stock:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente. Solo quedan {product.stock} unidades.")
                
                existing_item.quantity = new_qty
            else:
                # Si es nuevo, validamos cantidad inicial
                if item_data.quantity > product.stock:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente. Solo quedan {product.stock} unidades.")
                
                new_item = CartItemModel(cart_id=cart.id_key, product_id=item_data.product_id, quantity=item_data.quantity)
                db.add(new_item)
            
            # Guardamos cambios en el carrito, PERO NO TOCAMOS EL STOCK DEL PRODUCTO
            db.commit()
            return {"message": "Producto agregado al carrito"}

        # ELIMINAR ITEM (DELETE /api/v1/cart/{client_id}/items/{product_id})
        @self.router.delete("/{client_id}/items/{product_id}")
        async def remove_item(client_id: int, product_id: int, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart:
                return {"message": "Carrito no encontrado"}

            # Buscamos el item específico
            item = db.execute(select(CartItemModel).where(CartItemModel.cart_id == cart.id_key, CartItemModel.product_id == product_id)).scalar_one_or_none()
            
            if item:
                db.delete(item)
                db.commit()
            
            return {"message": "Producto eliminado del carrito"}
            
        # VACIAR CARRITO (DELETE /api/v1/cart/{client_id})
        @self.router.delete("/{client_id}")
        async def clear_cart(client_id: int, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if cart:
                # Borramos todos los items (gracias al cascade delete-orphan, si borramos items funciona)
                # O podemos borrar los items manualmente:
                db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id_key).delete()
                db.commit()
            return {"message": "Carrito vaciado"}