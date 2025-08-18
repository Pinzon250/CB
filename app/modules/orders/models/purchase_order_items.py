import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, ForeignKey, CheckConstraint, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_poi_qty_positive"),
        CheckConstraint("unit_cost >= 0 AND line_cost >= 0", name="chk_poi_costs_nonneg"),
        Index("idx_poi_po", "purchase_order_id"),
        {"schema": "orders"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.purchase_orders.id", ondelete="CASCADE"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("orders.order_items.id", ondelete="RESTRICT"), nullable=False)

    # Vinculo al mapeo del proveedor - producto/variante
    product_supplier_id = Column(UUID(as_uuid=True), ForeignKey("catalog.product_suppliers.id", ondelete="RESTRICT"), nullable=True)

    supplier_sku = Column(String, nullable=True) # snapshot
    quantity = Column(Integer, nullable=False, default=1)
    unit_cost = Column(Numeric(12, 2), nullable=False, default=0)
    line_cost = Column(Numeric(12, 2), nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
