import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cartitem_cart_product"),
        {"schema": "orders"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("orders.carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="RESTRICT"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)  # snapshot de precio al agregar al carrito
    line_total = Column(Numeric(12, 2), nullable=False)  # unit_price * quantity (calcular en servicio)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")  
