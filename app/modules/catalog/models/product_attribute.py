import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class ProductAttribute(Base):
    __tablename__ = "product_attributes"
    __table_args__ = {"schema": "catalog"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="CASCADE"))
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("catalog.attributes.id", ondelete="CASCADE"))
    value = Column(String, nullable=False)

    product = relationship("Product", back_populates="attributes")
    attribute = relationship("Attribute", back_populates="product_attributes")