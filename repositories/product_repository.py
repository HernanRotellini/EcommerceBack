"""Product repository with controlled relationship loading."""
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import or_, and_
from models.product import ProductModel
from repositories.base_repository_impl import BaseRepositoryImpl
from schemas.product_schema import ProductSchema


class ProductRepository(BaseRepositoryImpl):
    """Repository for Product entity with optimized loading."""

    def __init__(self, db: Session):
        super().__init__(ProductModel, ProductSchema, db)

    def find_all(self, skip: int = 0, limit: int = 100) -> List[ProductSchema]:
        """
        Get all products WITHOUT nested order_details.product circular reference.
        """
        products = (
            self.session.query(ProductModel)
            .options(
                # ✅ Carga category sin problemas
                joinedload(ProductModel.category),
                # ✅ Carga reviews sin problemas
                selectinload(ProductModel.reviews),
                # ❌ NO carga order_details para evitar ciclo
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # ✅ Convertir a schema usando model_validate
        return [ProductSchema.model_validate(product) for product in products]

    def find(self, id_key: int) -> ProductSchema:
        """
        Get single product WITHOUT loading nested order_details.product.
        """
        from models.order_detail import OrderDetailModel
        
        product = (
            self.session.query(ProductModel)
            .options(
                joinedload(ProductModel.category),
                selectinload(ProductModel.reviews),
                # ✅ SOLUCIÓN: Carga order_details pero NO el product anidado
                selectinload(ProductModel.order_details).lazyload(OrderDetailModel.product)
            )
            .filter(ProductModel.id_key == id_key)
            .first()
        )
        
        if not product:
            from repositories.base_repository_impl import InstanceNotFoundError
            raise InstanceNotFoundError(
                f"Product with id {id_key} not found"
            )
        
        return ProductSchema.model_validate(product)

    def filter_products(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
        sort_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductSchema]:
        """Filter products with optimized loading."""
        
        query = self.session.query(ProductModel).options(
            joinedload(ProductModel.category),
            selectinload(ProductModel.reviews),
            # Sin order_details para listados
        )

        # Apply filters
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    ProductModel.name.ilike(search_pattern),
                )
            )

        if category_id:
            query = query.filter(ProductModel.category_id == category_id)

        if min_price is not None:
            query = query.filter(ProductModel.price >= min_price)

        if max_price is not None:
            query = query.filter(ProductModel.price <= max_price)

        if in_stock_only:
            query = query.filter(ProductModel.stock > 0)

        # Sorting
        if sort_by == "price_asc":
            query = query.order_by(ProductModel.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(ProductModel.price.desc())
        elif sort_by == "name":
            query = query.order_by(ProductModel.name.asc())
        else:
            query = query.order_by(ProductModel.id_key.desc())

        products = query.offset(skip).limit(limit).all()
        return [ProductSchema.model_validate(product) for product in products]