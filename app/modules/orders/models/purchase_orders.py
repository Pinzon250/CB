import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey, CheckConstraint, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database.base import Base

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    __table_args__= (
        CheckConstraint("total_cost >= 0", name="chk_po_total_nonneg"),
        Index("idx_po_order_vendor", "order_id", "vendor_id"),
        {"schema": "orders"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE"), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("catalog.vendors.id", ondelete="RESTRICT"), nullable=False)
    
    status = Column(String, default="pending")
    total_cost = Column(Numeric(14,2), nullable=True, default=0)

    external_id = Column(String, nullable=True) # ID del PO en el sistema del proveedor
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)