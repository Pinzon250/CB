import uuid

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "catalog"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    Description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock =Column(Numeric, default=0)
    is_active =Column(Boolean, default=True)

    category_id = Column(UUID(as_uuid=True), ForeignKey("catalog.categories.id"))
    brand_id = Column(UUID(as_uuid=True), ForeignKey("catalog.brands.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
