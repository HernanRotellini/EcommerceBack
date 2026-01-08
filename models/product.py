from sqlalchemy import Column, Float, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class ProductModel(BaseModel):
    __tablename__ = 'products'

    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_product_stock_non_negative'),
    )

    name = Column(String, index=True)
    price = Column(Float, index=True)
    stock = Column(Integer, default=0, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id_key'), index=True)
    image_url = Column(String, nullable=True)

    category = relationship(
        'CategoryModel',
        back_populates='products',
        lazy='select',
    )
    reviews = relationship(
        'ReviewModel',
        back_populates='product',
        cascade='all, delete-orphan',
        lazy='select',
    )
    order_details = relationship(
        'OrderDetailModel',
        back_populates='product',
        cascade='all, delete-orphan',
        lazy='select',
    )