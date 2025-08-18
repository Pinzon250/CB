import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base

class ShipmentItem(Base):
    __tablename__ = "shipment_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_shipment_item_qty_positive"),
        UniqueConstraint("shipment_id", "order_item_id", name="uq_shipmentitem_unique_line"),
        {"schema": "shipping"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipping.shipments.id", ondelete="CASCADE"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("orders.order_items.id", ondelete="RESTRICT"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    shipment = relationship("Shipment", back_populates="items")
    order_item = relationship("OrderItem")