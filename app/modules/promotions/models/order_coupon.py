# models/promotions/order_coupon.py
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class OrderCoupon(Base):
    __tablename__ = "order_coupons"
    __table_args__ = (
        UniqueConstraint("order_id", "coupon_id", name="uq_order_coupon_once"),
        {"schema": "promotions"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id  = Column(UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE"), nullable=False)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("promotions.coupons.id", ondelete="CASCADE"), nullable=False)

    amount_applied = Column(Numeric(12,2), nullable=False, default=0)  # Lo que aporto el cupon al descuento total
    created_at = Column(DateTime, default=datetime.utcnow)
