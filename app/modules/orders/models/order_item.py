import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"schema": "orders"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("catalog.products.id", ondelete="RESTRICT"), nullable=False)

    # Snapshots del producto al momento de la compra
    product_name = Column(String, nullable=False)
    sku = Column(String, nullable=True) # (Stock Keeping Unit) 

    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10,2), nullable=False)
    line_total = Column(Numeric(12,2), nullable=False) # unit_price * quantity (calcular en servicio)

    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")