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
        
        # OBTENER CARRITO
        @self.router.get("/{client_id}", response_model=CartResponse)
        async def get_cart(client_id: int, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart:
                cart = CartModel(client_id=client_id)
                db.add(cart)
                db.commit()
                db.refresh(cart)
            
            # Calculamos total (evitando errores si product es None)
            total = sum(item.quantity * item.product.price for item in cart.items if item.product)
            response = CartResponse.model_validate(cart)
            response.total = total
            return response

        # AGREGAR (SUMAR) ITEM
        @self.router.post("/{client_id}/items")
        async def add_item(client_id: int, item_data: CartItemBase, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart:
                cart = CartModel(client_id=client_id)
                db.add(cart)
                db.commit()
                db.refresh(cart)

            product = db.query(ProductModel).get(item_data.product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            existing_item = next((i for i in cart.items if i.product_id == item_data.product_id), None)
            
            if existing_item:
                new_qty = existing_item.quantity + item_data.quantity
                if new_qty > product.stock:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente. Máximo: {product.stock}")
                existing_item.quantity = new_qty
            else:
                if item_data.quantity > product.stock:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente. Máximo: {product.stock}")
                new_item = CartItemModel(cart_id=cart.id_key, product_id=item_data.product_id, quantity=item_data.quantity)
                db.add(new_item)
            
            db.commit()
            return {"message": "Item agregado"}

        # ACTUALIZAR CANTIDAD EXACTA (Para el Checkout)
        @self.router.put("/{client_id}/items")
        async def update_item(client_id: int, item_data: CartItemBase, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart: return {"message": "Carrito no encontrado"}

            item = next((i for i in cart.items if i.product_id == item_data.product_id), None)
            if not item:
                 raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")

            product = db.query(ProductModel).get(item_data.product_id)
            if item_data.quantity > product.stock:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente. Máximo: {product.stock}")

            item.quantity = item_data.quantity
            db.commit()
            return {"message": "Cantidad actualizada"}

        # ELIMINAR ITEM
        @self.router.delete("/{client_id}/items/{product_id}")
        async def remove_item(client_id: int, product_id: int, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if not cart: return {"message": "Carrito no encontrado"}

            # Nota: Usamos ejecución directa de delete para asegurar limpieza
            db.query(CartItemModel).filter(
                CartItemModel.cart_id == cart.id_key, 
                CartItemModel.product_id == product_id
            ).delete()
            db.commit()
            return {"message": "Item eliminado"}
            
        # VACIAR CARRITO
        @self.router.delete("/{client_id}")
        async def clear_cart(client_id: int, db: Session = Depends(get_db)):
            cart = db.execute(select(CartModel).where(CartModel.client_id == client_id)).scalar_one_or_none()
            if cart:
                db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id_key).delete()
                db.commit()
            return {"message": "Carrito vaciado"}